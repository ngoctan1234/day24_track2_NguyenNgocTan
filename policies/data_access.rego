package medviet.access

default allow = false

allow {
    input.role == "admin"
}

allow {
    input.role == "ml_engineer"
    input.resource == "training_data"
    input.action == "read"
}

allow {
    input.role == "ml_engineer"
    input.resource == "aggregated_metrics"
    input.action == "read"
}

allow {
    input.role == "data_analyst"
    input.resource == "aggregated_metrics"
    input.action == "read"
}

allow {
    input.role == "intern"
    input.resource == "sandbox_data"
    input.action == "read"
}

deny_reason := "Raw patient data requires admin role" {
    input.resource == "patient_data"
    input.role != "admin"
}
