terraform {
  required_providers {
    rustack = {
      source  = "pilat/rustack"
      version = "> 1.1.0"
    }
  }
}


provider "rustack" {
    api_endpoint = "https://cloud.mephi.ru"
    token = "10bf108dc1de044c960f74fa50ad08b8f286900a"
}

data "rustack_project" "my_project" {
    name = "Лаб 1"
}

# Получение параметров доступного гипервизора KVM (сегмент РУСТЭК) по его имени и по id проекта (шаг 3)
data "rustack_hypervisor" "kvm" {
    project_id = data.rustack_project.my_project.id
    name = "РУСТЭК"
}

# Создание ВЦОД РУСТЭК.
# Задаём его имя, указываем id проекта, который получили на шаге 2 при обращении к data source rustack_project
# Указываем id гипервизора, который получили на шаге 3 при обращении к data source rustack_hypervisor (шаг 4)
resource "rustack_vdc" "vdc1" {
    name = "KVM Terraform"
    project_id = data.rustack_project.my_project.id
    hypervisor_id = data.rustack_hypervisor.kvm.id
}

# Получение параметров автоматически созданной при создании ВЦОД сервисной сети по её имени и id созданного ВЦОД, который получили на шаге 4 при создании resource rustack_vdc (шаг 5)
data "rustack_network" "service_network" {
    vdc_id = resource.rustack_vdc.vdc1.id
    name = "Сеть"
}

# Получение параметров доступного типа дисков по его имени и id созданного ВЦОД, который получили на шаге 4 при создании resource rustack_vdc (шаг 6)
data "rustack_storage_profile" "ssd" {
    vdc_id = resource.rustack_vdc.vdc1.id
    name = "ssd"
}

# Получение параметров доступного шаблона ОС по его имени и id созданного ВЦОД, который получили на шаге 4 при создании resource rustack_vdc (шаг 7)
data "rustack_template" "ubuntu20" {
    vdc_id = resource.rustack_vdc.vdc1.id
    name = "Ubuntu 20.04"
}

# Получение параметров доступного шаблона брандмауэра по его имени и id созданного ВЦОД, который получили на шаге 4 при создании resource rustack_vdc (шаг 8)
data "rustack_firewall_template" "allow_default" {
    vdc_id = resource.rustack_vdc.vdc1.id
    name = "Разрешить исходящие"
}


data "rustack_firewall_template" "allow_ssh" {
    vdc_id = resource.rustack_vdc.vdc1.id
    name = "Разрешить SSH"
}
# # Создание порта сервера (шаг 9)
# # Указываем ВЦОД в котором порт будет создан, сеть к которой он должен быть присоединён и IP-адрес, а также шаблон брандмауэра

resource "rustack_port" "vm_port" {
    vdc_id = resource.rustack_vdc.vdc1.id

    network_id = data.rustack_network.service_network.id
    ip_address = "10.0.1.20"
    firewall_templates = [data.rustack_firewall_template.allow_default.id, data.rustack_firewall_template.allow_ssh.id]
}


# # Создание сервера.
# # Задаём его имя и конфигурацию. Выбираем шаблон ОС по его id, который получили на шаге 7. Ссылаемся на скрипт инициализации. Указываем размер и тип основного диска.
# # Выбираем порт сервера созданный на шаге 9
# # Указываем, что необходимо получить публичный адрес.
resource "rustack_vm" "vm" {
    vdc_id = resource.rustack_vdc.vdc1.id
    name = "Server 1"
    cpu = 4
    ram = 4

    template_id = data.rustack_template.ubuntu20.id

    user_data = file("cloud-config.yaml")

    system_disk {
        size = 10
        storage_profile_id = data.rustack_storage_profile.ssd.id
    }

    ports = [resource.rustack_port.vm_port.id]

    floating = true

     provisioner "file" {
    source      = "../docker"
    destination = "/home/api/docker"
  }
       provisioner "file" {
    source      = "./init.sh"
    destination = "/home/api/init.sh"
  }
  provisioner "remote-exec" {
    inline = [ "bash /home/api/init.sh" ]
  }

}