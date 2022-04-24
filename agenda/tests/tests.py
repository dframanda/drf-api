import json
from datetime import datetime, timezone
from unittest import mock
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase

from agenda.models import Agendamento, Estabelecimento, Funcionarios, Servicos

# Create your tests here.


class TestPermissoes(APITestCase):
    def test_retorna_false_has_permission(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        resposta_permissao = {
            "detail": "You do not have permission to perform this action."
        }

        url = "/api/agendamentos/"
        response = self.client.get(url + "?username=maria")
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(data, resposta_permissao)


class TestValidacoes(APITestCase):
    def test_retorna_username_incorreto(self):
        servico = Servicos.objects.create(servico="Manicure")

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        agendamento_request = {
            "prestador": "mario",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-22T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        resposta_agendamento = {"prestador": ["Username incorreto!"]}

        response = self.client.post(
            "/api/agendamentos/?username=mario",
            agendamento_request,
            prestador="mario",
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)

    def test_retorna_estabelecimento_nao_existe(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        servico = Servicos.objects.create(servico="Manicure")

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        resposta_agendamento = {"estabelecimento": ["Estabelecimento não encontrado!"]}

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento="Salão de Beleza",
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)

    def test_retorna_servico_nao_encontrado(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        resposta_agendamento = {"servico": ["Serviço não encontrado!"]}

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico="Manicure",
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)

    def test_retorna_agendamento_nao_pode_ser_feito_no_passado(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        servico = Servicos.objects.create(servico="Manicure")

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2022-01-01T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        resposta_agendamento = {
            "data_horario": ["Agendamento não pode ser feito no passado!"]
        }

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)

    def test_retorna_funcionario_estabelecimento_ou_servico_nao_existem(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        servico = Servicos.objects.create(servico="Manicure")
        servico_nao_feito = Servicos.objects.create(servico="Pedicure")

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Pedicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        resposta_agendamento = {
            "non_field_errors": [
                "Funcionário, estabelecimento ou serviço não estão corretos ou não existem!"
            ]
        }

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico_nao_feito,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)


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
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        servico = Servicos.objects.create(servico="Manicure")

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        Agendamento.objects.create(
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            data_horario=datetime(2023, 12, 20, 15, tzinfo=timezone.utc),
            nome_cliente="Virginia",
            email_cliente="virginia@email.com",
            telefone_cliente="123123123",
        )

        agendamento_serializado = {
            "id": 1,
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
            "states": "UNCO",
            "cancelado": False,
        }

        url = "/api/agendamentos/"
        response = self.client.get(url + "?username=silvia")
        data = json.loads(response.content)
        self.assertDictEqual(data[0], agendamento_serializado)


class TestCriacaoAgendamento(APITestCase):
    def test_cria_agendamento(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        servico = Servicos.objects.create(servico="Manicure")

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        Agendamento.objects.create(
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            data_horario=datetime(2023, 12, 20, 15, tzinfo=timezone.utc),
            nome_cliente="Virginia",
            email_cliente="virginia@email.com",
            telefone_cliente="123123123",
        )

        agendamento_criado = Agendamento.objects.get()

        self.assertEqual(
            agendamento_criado.data_horario,
            datetime(2023, 12, 20, 15, tzinfo=timezone.utc),
        )

    def test_quando_request_e_invalido_retorna_400(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        servico = Servicos.objects.create(servico="Manicure")

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request_domingo = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-24T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request_domingo,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_quando_agendamento_confirmado_retorna_indisponivel(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        servico = Servicos.objects.create(servico="Manicure")

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        Agendamento.objects.create(
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            data_horario=datetime(2023, 12, 20, 15, tzinfo=timezone.utc),
            nome_cliente="Virginia",
            email_cliente="virginia@email.com",
            telefone_cliente="123123123",
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        url = "/api/agendamentos/1/?username=silvia"

        self.client.patch(url, {"states": "CONF"})

        agendamento_request_mesma_data = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        resposta_serializada = {"data_horario": ["Este horário não está disponível!"]}

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(resposta_serializada, data)

    def test_cada_cliente_pode_ter_uma_reserva_por_dia(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        servico = Servicos.objects.create(servico="Manicure")

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T13:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        agendamento_request_mesmo_dia = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        resposta_agendamento = {
            "non_field_errors": ["Cada cliente pode ter apenas uma reverva por dia!"]
        }

        self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request_mesmo_dia,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)

    def test_email_brasileiro_deve_estar_associado_a_numero_brasilerio(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        servico = Servicos.objects.create(servico="Manicure")

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com.br",
            "telefone_cliente": "+33123123123",
        }

        resposta_agendamento = {
            "non_field_errors": [
                "E-mail brasileiro deve estar associado a um número do Brasil (+55)"
            ]
        }

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)

    def test_telefone_precisa_conter_minimo_oito_digitos(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        servico = Servicos.objects.create(servico="Manicure")

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com.br",
            "telefone_cliente": "123",
        }

        resposta_agendamento = {
            "telefone_cliente": ["Telefone precisa conter no mínimo 8 dígitos"]
        }

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)

    def test_retorna_telefone_formato_invalido(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        servico = Servicos.objects.create(servico="Manicure")

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com.br",
            "telefone_cliente": "1231+23123",
        }

        resposta_agendamento = {"telefone_cliente": ["Formato inválido"]}

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)

    def test_numero_precisa_ser_composto_por_digitos(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        servico = Servicos.objects.create(servico="Manicure")

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com.br",
            "telefone_cliente": "abcd^efg~h",
        }

        resposta_agendamento = {
            "telefone_cliente": ["Telefone deve ser composto por dígitos!"]
        }

        response = self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)


class TestMostraDetalheAgendamento(APITestCase):
    def test_mostra_agendamento(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        servico = Servicos.objects.create(servico="Manicure")

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        Agendamento.objects.create(
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            data_horario=datetime(2023, 12, 20, 15, tzinfo=timezone.utc),
            nome_cliente="Virginia",
            email_cliente="virginia@email.com",
            telefone_cliente="123123123",
        )

        agendamento_serializado = {
            "id": 1,
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
            "states": "UNCO",
            "cancelado": False,
        }

        url = "/api/agendamentos/1/"
        response = self.client.get(url + "?username=silvia")
        data = json.loads(response.content)
        self.assertDictEqual(data, agendamento_serializado)

    def test_quando_request_inexistente_retorna_404(self):
        response = self.client.get("/api/agendamentos/1/")

        self.assertEqual(response.status_code, 404)


class TestEditaAgendamento(APITestCase):
    def test_edita_agendamento(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        servico = Servicos.objects.create(servico="Manicure")

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        Funcionarios.objects.create(
            prestador=user, estabelecimento=estabelecimento, servico=servico
        )

        agendamento_request = {
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
        }

        agendamento_serializado_editado = {
            "id": 1,
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia W.",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
            "states": "UNCO",
            "cancelado": False,
        }

        self.client.post(
            "/api/agendamentos/?username=silvia",
            agendamento_request,
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            format="json",
        )

        url = "/api/agendamentos/1/?username=silvia"
        response_patch = self.client.patch(url, {"nome_cliente": "Virginia W."})
        response_get = self.client.get(url)

        data = json.loads(response_get.content)

        self.assertEqual(agendamento_serializado_editado, data)
        self.assertEqual(response_patch.status_code, 200)


class TestCancelaAgendamento(APITestCase):
    def test_cancela_agendamento(self):
        user = User.objects.create(
            email="silvia@email.com", username="silvia", password="123"
        )
        self.client.force_authenticate(user)

        servico = Servicos.objects.create(servico="Manicure")

        estabelecimento = Estabelecimento.objects.create(
            nome_estabelecimento="Salão de Beleza"
        )

        Agendamento.objects.create(
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            data_horario=datetime(2023, 12, 20, 15, tzinfo=timezone.utc),
            nome_cliente="Virginia",
            email_cliente="virginia@email.com",
            telefone_cliente="123123123",
        )

        agendamento_serializado = {
            "id": 1,
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T15:00:00Z",
            "nome_cliente": "Virginia",
            "email_cliente": "virginia@email.com",
            "telefone_cliente": "123123123",
            "states": "UNCO",
            "cancelado": False,
        }

        Agendamento.objects.create(
            prestador=user,
            estabelecimento=estabelecimento,
            servico=servico,
            data_horario=datetime(2023, 12, 20, 17, tzinfo=timezone.utc),
            nome_cliente="Silvia",
            email_cliente="silvia@email.com",
            telefone_cliente="123123123",
        )

        agendamento_serializado_dois = {
            "id": 2,
            "prestador": "silvia",
            "estabelecimento": "Salão de Beleza",
            "servico": "Manicure",
            "data_horario": "2023-12-20T17:00:00Z",
            "nome_cliente": "Silvia",
            "email_cliente": "silvia@email.com",
            "telefone_cliente": "123123123",
            "states": "UNCO",
            "cancelado": False,
        }

        self.client.delete(
            "/api/agendamentos/2/?username=silvia",
            agendamento_serializado_dois,
            format="json",
        )
        get_response = self.client.get("/api/agendamentos/?username=silvia")
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


class TestGetHorarios(APITestCase):
    @mock.patch("agenda.libs.brasil_api.is_feriado", return_value=True)
    def test_quando_data_e_feriado_retorna_lista_vazia(self, _):
        response = self.client.get("/api/horarios/?data=2022-04-15")
        data = json.loads(response.content)

        self.assertEqual(data, [])

    @mock.patch("agenda.libs.brasil_api.is_feriado", return_value=False)
    def test_quando_data_e_dia_util_retorna_lista_com_horarios(self, _):
        response = self.client.get("/api/horarios/?data=2022-12-20")
        data = json.loads(response.content)

        self.assertNotEqual(data, [])
        self.assertEqual(data[0], "2022-12-20T09:00:00Z")
        self.assertEqual(data[-1], "2022-12-20T17:30:00Z")


class TestCriacaoServico(APITestCase):
    def test_retorna_servico(self):
        user = User.objects.create(
            email="maria@email.com", username="maria", password="123"
        )
        self.client.force_authenticate(user)

        user.is_staff = True

        servico_request = {"servico": "Manicure"}

        servico_serializado = {"id": 1, "servico": "Manicure"}

        response = self.client.post("/api/servicos/", servico_request, format="json")

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(data, servico_serializado)

    def test_retorna_o_servico_ja_existe(self):
        user = User.objects.create(
            email="maria@email.com", username="maria", password="123"
        )
        self.client.force_authenticate(user)

        user.is_staff = True

        servico = Servicos.objects.create(servico="Manicure")

        servico_request = {"servico": "Manicure"}

        resposta_agendamento = {"non_field_errors": ["O serviço informado já existe!"]}

        response = self.client.post("/api/servicos/", servico_request, format="json")

        data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(data, resposta_agendamento)
