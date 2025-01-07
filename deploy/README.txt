In baseball-prod, the following secret must be created before the app will deploy

oc create secret generic kubeconfig-secret --from-file config

