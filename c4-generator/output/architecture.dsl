workspace {
    model {
        user = person "User" {
            description "System User"
        }

        VaulPay = softwareSystem "VaulPay" {
            description "Spring Boot Microservice"
            tags "Microservice"
        }
    }

    views {
        systemLandscape "SystemLandscape" {
            include *
            autolayout lr
        }

        systemContext VaulPay "SystemContext_VaulPay" {
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