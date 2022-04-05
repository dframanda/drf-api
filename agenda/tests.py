import json
from datetime import datetime, timezone

from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase

from agenda.models import Agendamento

# Create your tests here.


class TestListagemAgendamentos(APITestCase):
    def test_listagem_vazia(self):
        user = User.objects.create(
            email="maria@email.com", username="maria", password="123"
        )
        self.client.force_authenticate(user)

        url = "/api/agendamentos/"
        response = self.client.get(url + "?username=maria")
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_listagem_de_agendamentos_criados(self):
        user = User.objects.create(
            email="pherb@email.com", username="pherb", password="123"
        )
        self.client.force_authenticate(user)

        Agendamento.objects.create(
            data_horario=datetime(2022, 3, 31, tzinfo=timezone.utc),
            nome_cliente="Pherb",
            email_cliente="pherb@email.com",
            telefone_cliente="123123123",
            prestador=user,
        )

        agendamento_serializado = {
            "id": 1,
            "data_horario": "2022-03-31T00:00:00Z",
            "nome_cliente": "Pherb",
            "email_cliente": "pherb@email.com",
            "telefone_cliente": "123123123",
            "prestador": "pherb",
        }

        url = "/api/agendamentos/"
        response = self.client.get(url + "?username=pherb")
        data = json.loads(response.content)
        self.assertDictEqual(data[0], agendamento_serializado)


class TestCriacaoAgendamento(APITestCase):
    def test_cria_agendamento(self):
        user = User.objects.create(
            email="pherb@email.com", username="pherb", password="123"
        )
        self.client.force_authenticate(user)

        agendamento_request_data = {
            "data_horario": "2022-04-05T15:00:00Z",
            "nome_cliente": "Pherb",
            "email_cliente": "pherb@email.com",
            "telefone_cliente": "123123123",
            "prestador": "pherb",
        }

        response = self.client.post(
            "/api/agendamentos/?username=pherb",
            agendamento_request_data,
            prestador=user,
            format="json",
        )
        agendamento_criado = Agendamento.objects.get()

        self.assertEqual(
            agendamento_criado.data_horario,
            datetime(2022, 4, 5, 15, tzinfo=timezone.utc),
        )
        self.assertEqual(response.status_code, 201)

    def test_quando_request_e_invalido_retorna_400(self):
        agendamento_request_domingo = {
            "data_horario": "2022-04-03T15:00:00Z",
            "nome_cliente": "Pherb",
            "email_cliente": "pherb@email.com",
        }
        response = self.client.post(
            "/api/agendamentos/", agendamento_request_domingo, format="json"
        )

        self.assertEqual(response.status_code, 400)


class TestMostraDetalheAgendamento(APITestCase):
    def test_mostra_agendamento(self):
        user = User.objects.create(
            email="preb@email.com", username="pherb", password="123"
        )
        self.client.force_authenticate(user)

        Agendamento.objects.create(
            data_horario=datetime(2022, 5, 11, 15, tzinfo=timezone.utc),
            nome_cliente="Pherb",
            email_cliente="pherb@email.com",
            telefone_cliente="123123123",
            prestador=user,
        )

        agendamento_serializado = {
            "id": 1,
            "data_horario": "2022-05-11T15:00:00Z",
            "nome_cliente": "Pherb",
            "email_cliente": "pherb@email.com",
            "telefone_cliente": "123123123",
            "prestador": "pherb",
        }

        url = "/api/agendamentos/1/"
        response = self.client.get(url + "?username=pherb")
        data = json.loads(response.content)
        self.assertDictEqual(data, agendamento_serializado)

    def test_quando_request_inexistente_retorna_404(self):
        response = self.client.get("/api/agendamentos/1/")

        self.assertEqual(response.status_code, 404)


class TestEditaAgendamento(APITestCase):
    def test_edita_agendamento(self):
        user = User.objects.create(
            email="pherb@email.com", username="pherb", password="123"
        )
        self.client.force_authenticate(user)

        agendamento_request_data = {
            "data_horario": "2022-04-04T15:00:00Z",
            "nome_cliente": "Pherb",
            "email_cliente": "pherb@email.com",
            "telefone_cliente": "123123123",
            "prestador": "pherb",
        }

        agendamento_serializado_editado = {
            "id": 1,
            "data_horario": "2022-04-04T15:00:00Z",
            "nome_cliente": "Pherb Brehp",
            "email_cliente": "pherb@email.com",
            "telefone_cliente": "123123123",
            "prestador": "pherb",
        }

        self.client.post(
            "/api/agendamentos/?username=pherb", agendamento_request_data, format="json"
        )
        url = "/api/agendamentos/1/"
        response_patch = self.client.patch(url, {"nome_cliente": "Pherb Brehp"})
        response_get = self.client.get(url + "?username=pherb")
        data = json.loads(response_get.content)

        self.assertEqual(agendamento_serializado_editado, data)
        self.assertEqual(response_patch.status_code, 200)


class TestCancelaAgendamento(APITestCase):
    def test_cancela_agendamento(self):
        user = User.objects.create(
            email="pherb@email.com", username="pherb", password="123"
        )
        self.client.force_authenticate(user)

        Agendamento.objects.create(
            data_horario=datetime(2022, 3, 31, 16, tzinfo=timezone.utc),
            nome_cliente="Pherb",
            email_cliente="pherb@email.com",
            telefone_cliente="123123123",
            prestador=user,
        )

        Agendamento.objects.create(
            data_horario=datetime(2022, 4, 6, 14, tzinfo=timezone.utc),
            nome_cliente="Maria",
            email_cliente="maria@email.com",
            telefone_cliente="321321321",
            prestador=user,
        )

        agendamento_serializado = {
            "id": 1,
            "data_horario": "2022-03-31T16:00:00Z",
            "nome_cliente": "Pherb",
            "email_cliente": "pherb@email.com",
            "telefone_cliente": "123123123",
            "prestador": "pherb",
        }
        agendamento_serializado_dois = {
            "id": 2,
            "data_horario": "2022-04-06T14:00:00Z",
            "nome_cliente": "Maria",
            "email_cliente": "maria@email.com",
            "telefone_cliente": "321321321",
            "prestador": "pherb",
        }

        self.client.delete(
            "/api/agendamentos/2/?username=pherb",
            agendamento_serializado_dois,
            format="json",
        )
        get_response = self.client.get("/api/agendamentos/?username=pherb")
        data = json.loads(get_response.content)

        self.assertEqual(agendamento_serializado, data[0])


class TestListagemPrestadores(APITestCase):
    def test_lista_prestadores(self):
        user = User.objects.create(
            email="maria@email.com", username="maria", password="123"
        )
        self.client.force_authenticate(user)

        prestador_criado = User.objects.get()

        self.assertEqual("maria", prestador_criado.username)
        self.assertEqual("maria@email.com", prestador_criado.email)
