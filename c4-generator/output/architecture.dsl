workspace {
    model {
        VaulPay = softwareSystem "VaulPay" {
            description "Spring Boot Microservice"
            tags "Microservice"
        }
    }

    views {
        systemContext {
            include *
            autolayout lr
        }

        styles {
            element "Microservice" {
                background #1168bd
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #438dd5
                color #ffffff
            }
        }
    }
}