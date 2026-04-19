#!/bin/bash
set -euo pipefail
IFS=$'\n\t'
 
DOCKER_DNS_RULES=$(iptables-save -t nat | grep "127\.0\.0\.11" || true)
 
iptables -F && iptables -X
iptables -t nat -F && iptables -t nat -X
iptables -t mangle -F && iptables -t mangle -X
ipset destroy allowed-domains 2>/dev/null || true
 
if [ -n "$DOCKER_DNS_RULES" ]; then
    iptables -t nat -N DOCKER_OUTPUT 2>/dev/null || true
    iptables -t nat -N DOCKER_POSTROUTING 2>/dev/null || true
    echo "$DOCKER_DNS_RULES" | xargs -L 1 iptables -t nat
fi
 
# Permite DNS + SSH + localhost
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p udp --sport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
 
# Cria whitelist
ipset create allowed-domains hash:net
 
# GitHub IPs
gh_ranges=$(curl -s https://api.github.com/meta)
[ -z "$gh_ranges" ] && echo "ERROR: Failed to fetch GitHub IP ranges" && exit 1
echo "$gh_ranges" | jq -e '.web and .api and .git' >/dev/null || exit 1
 
while read -r cidr; do
    [[ "$cidr" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$ ]] || exit 1
    ipset add allowed-domains "$cidr"
done < <(echo "$gh_ranges" | jq -r '(.web + .api + .git)[]' | aggregate -q)
 
# Outros domínios essenciais
for domain in \
    "registry.npmjs.org" \
    "pypi.org" \
    "files.pythonhosted.org" \
    "pythonhosted.org" \
    "api.anthropic.com" \
    "sentry.io" \
    "statsig.anthropic.com" \
    "statsig.com" \
    "marketplace.visualstudio.com" \
    "vscode.blob.core.windows.net" \
    "update.code.visualstudio.com"; do
    ips=$(dig +noall +answer A "$domain" | awk '$4 == "A" {print $5}')
    [ -z "$ips" ] && echo "ERROR: Failed to resolve $domain" && exit 1
    while read -r ip; do
        ipset add allowed-domains "$ip"
    done < <(echo "$ips")
done

# Dominios adicionais (ex.: pooler do Supabase) via variavel de ambiente.
if [ -n "${DB_HOST:-}" ]; then
    EXTRA_ALLOWED_DOMAINS="${EXTRA_ALLOWED_DOMAINS:-},${DB_HOST}"
fi

if [ -n "${EXTRA_ALLOWED_DOMAINS:-}" ]; then
    IFS=',' read -ra extra_domains <<< "$EXTRA_ALLOWED_DOMAINS"
    for domain in "${extra_domains[@]}"; do
        domain_trimmed="$(echo "$domain" | xargs)"
        [ -z "$domain_trimmed" ] && continue
        ips=$(dig +noall +answer A "$domain_trimmed" | awk '$4 == "A" {print $5}')
        [ -z "$ips" ] && echo "ERROR: Failed to resolve $domain_trimmed" && exit 1
        while read -r ip; do
            ipset add allowed-domains "$ip"
        done < <(echo "$ips")
    done
fi
 
# Rede do host Docker
HOST_IP=$(ip route | grep default | cut -d" " -f3)
HOST_NETWORK=$(echo "$HOST_IP" | sed "s/\.[0-9]*$/.0\/24/")
iptables -A INPUT -s "$HOST_NETWORK" -j ACCEPT
iptables -A OUTPUT -d "$HOST_NETWORK" -j ACCEPT
 
# 🔒 POLÍTICA PADRÃO: BLOQUEIA TUDO
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
 
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m set --match-set allowed-domains dst -j ACCEPT
iptables -A OUTPUT -j REJECT --reject-with icmp-admin-prohibited
 
# Verificação
echo "Firewall configuration complete"
if curl --connect-timeout 5 https://example.com >/dev/null 2>&1; then
    echo "ERROR: Firewall FALHOU — conseguiu acessar example.com" && exit 1
else
    echo "✅ Firewall OK — example.com bloqueado"
fi
if ! curl --connect-timeout 5 https://api.github.com/zen >/dev/null 2>&1; then
    echo "ERROR: Firewall FALHOU — não consegue acessar GitHub" && exit 1
else
    echo "✅ Firewall OK — GitHub acessível"
fi