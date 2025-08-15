#!/bin/bash
echo "=== Vérification Configuration Airport Project ==="

echo "📍 Conteneurs Docker:"
docker-compose ps

echo -e "\n🔌 Ports utilisés:"
echo "PostgreSQL (5433):"
ss -tulpn | grep :5433 && echo "  ✓ 5433: Airport PostgreSQL" || echo "  ○ 5433: Libre"
echo "pgAdmin (8081):"
ss -tulpn | grep :8081 && echo "  ✓ 8081: Airport pgAdmin" || echo "  ○ 8081: Libre"
echo "Redis (6380):"
ss -tulpn | grep :6380 && echo "  ✓ 6380: Airport Redis" || echo "  ○ 6380: Libre"

echo -e "\n💾 Volumes Docker:"
docker volume ls | grep airport

echo -e "\n🌐 Networks Docker:"
docker network ls | grep airport

echo -e "\n🧪 Test connexion PostgreSQL:"
docker-compose exec -T postgres psql -U airport_user -d airport_air_quality -c "SELECT 'Connection OK' as status;"

echo -e "\n🧪 Test connexion Redis:"
docker-compose exec -T redis redis-cli ping

echo -e "\n✅ Configuration vérifiée !"
