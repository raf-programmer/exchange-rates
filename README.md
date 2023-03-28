# exchange-rates
Aplikacja jest zbudowana w oparciu o k8s, jej elementy uruchamiane są w podach.
Pody kubernetesowe można uruchamiać w różny sposób, poniżej podaję instrukcję do uruchomienia aplikacji za pomocą minikube https://minikube.sigs.k8s.io/docs/

1. Uruchamiamy części składowe aplikacji:
kubectl apply -f k8s/namespace/
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/code/
kubectl apply -f k8s/caller/
kubectl apply -f k8s/nginx/

2. Uruchamiane pody i ich status można zaobserwować za pomocą komendy: kubectl get pods -n fastapi-project -w

3. Naniesienie migracji bazy exchange_rates:
kubectl apply -f k8s/job/migration.yml
kubectl apply -f k8s/job/secret.yml

4. Naniesienie migracji bazy calls:
a) Wejść do poda podając w komendzie postgres-deployment-unikatowe-id-poda np: kubectl exec -it postgres-deployment-przyklad-abcd bash -n fastapi-project
b) Utworzenie bazy będąc w podzie postgres-deployment: createdb -U rafiki calls
c) Po wyjściu z poda nanosimy migracje do bazy calls komendami:
kubectl apply -f k8s/job/caller-migration.yml
kubectl apply -f k8s/job/caller-secret.yml

5. Listę serwisów można wyświetlić komendą: minikube service list (podany url). Na podanym urlu ze ścieżką /docs np. http://192.168.49.2:30009/docs znajduje się swagger ui z endpointami exchange_rates.
Można czekać na zapis kursów walut, który dokonuje się o 6 i 18, a można wywołać za pomocą swagger ui endpoint /exchange_rates/save_current do zapisu.

6. Wywoływanie przeliczenia walut - wejść do poda caller-deployment np: kubectl exec -it caller-deployment-796c74fc97-thx5x bash -n fastapi-project (w środku będziemy wywoływać poniższe komendy do przeliczenia walut).
a) Komenda do wyświetlenia listy calls:
curl -X 'GET' \
  'http://127.0.0.1:5000/caller/' \
  -H 'accept: application/json'
b) Komenda do przeliczenia waluty bez daty:
curl -X 'POST' \
  'http://127.0.0.1:5000/caller/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "from_currency": "USD",
  "to_currency": "AUD",
  "amount": 350
}'
c) Komenda do przeliczenia waluty z datą:
curl -X 'POST' \
  'http://127.0.0.1:5000/caller/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "from_currency": "USD",
  "to_currency": "AUD",
  "amount": 100,
  "when": "2023-03-27T20:36:19"
}'
7. Lista wspieranych walut: ["PLN", "THB", "USD", "AUD", "HKD", "CAD", "NZD", "SGD", "EUR", "HUF", "CHF", "GBP", "UAH", "JPY", "CZK", "DKK", "ISK", "NOK", "SEK", "RON", "BGN", "TRY", "ILS", "CLP", "PHP", "MXN", "ZAR", "BRL", "MYR", "IDR", "INR", "KRW", "CNY", "XDR"]
