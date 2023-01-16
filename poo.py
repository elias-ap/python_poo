import typing
import xml.etree.ElementTree as Et


codigoProcedimento = '41101014'
codigoDespesa = '90289870'


class ContaTiss:
    corpoGuia: Et.Element
    guias: typing.Generator
    ans_prefix = {"ans": "http://www.ans.gov.br/padroes/tiss/schemas"}

    def __init__(self):
        caminhoGuia = r"00000000000000011306_92a0e8826a52304e3ac85dfe30c83f38.xml"
        self.corpoGuia = Et.parse(caminhoGuia, parser=Et.XMLParser(encoding="ISO-8859-1")).getroot()
        self.guias = self.corpoGuia.find('.//ans:guiasTISS', self.ans_prefix)

    def setCorpoGuia(self, corpo):
        self.setCorpoGuia(corpo)

    def getCorpoGuia(self):
        return self.corpoGuia


class Guia:
    numeroGuia: Et.ElementTree
    guia: Et.ElementTree
    procedimentosExecutados: Et.ElementTree
    outrasDespesas: Et.ElementTree
    dadosProcedimento: [Et.ElementTree]
    dadosDespesa: [Et.ElementTree]
    ans_prefix = ContaTiss.ans_prefix
    proc: str

    def __init__(self, guia, p):
        self.setNumeroGuia(guia)
        self.setGuia(guia)
        self.proc = p
        self.setProcedimentosExecutados(guia)
        self.setOutrasDespesas(guia)
        self.setListaProcedimentos()
        self.setListaDespesa()

    def setNumeroGuia(self, guia: str):
        self.numeroGuia = guia.find('.//ans:cabecalhoGuia/ans:numeroGuiaPrestador', self.ans_prefix).text

    def getNumeroGuia(self):
        return self.numeroGuia

    def setGuia(self, guia):
        self.guia = guia

    def getGuia(self):
        return self.guia

    def setProcedimentosExecutados(self, guia):
        self.procedimentosExecutados = guia.find('ans:procedimentosExecutados', self.ans_prefix)

    def getProcedimentosExecutados(self):
        return self.procedimentosExecutados

    def setOutrasDespesas(self, guia):
        self.outrasDespesas = guia.find('ans:outrasDespesas', self.ans_prefix)

    def getOutrasDespesas(self):
        return self.outrasDespesas

    def setListaProcedimentos(self):
        if Et.iselement(self.getProcedimentosExecutados()):
            self.dadosProcedimento = list(self.getProcedimentosExecutados().iterfind(
                f'.//ans:procedimento[ans:codigoProcedimento="{self.proc}"]..', self.ans_prefix))

    def getListaProcedimento(self):
        return self.dadosProcedimento

    def setListaDespesa(self):
        if Et.iselement(self.getOutrasDespesas()):
            self.dadosDespesa = list(self.getOutrasDespesas().iterfind(
                f'.//ans:servicosExecutados[ans:codigoProcedimento="{self.proc}"]..', self.ans_prefix))

    def getListaDespesa(self):
        return self.dadosDespesa

    def alteraValorTotalGeral(self, diferenca):
        valoresTotais = self.getGuia().find('ans:valorTotal', self.ans_prefix)
        valorTotalGeral = valoresTotais.find('ans:valorTotalGeral', self.ans_prefix)

        for valorTotal in valoresTotais:
            if float(valorTotal.text) > diferenca:
                valorTotal.text = '%.2f' % (float(valorTotal.text) - diferenca)
                valorTotalGeral.text = '%.2f' % (float(valorTotalGeral.text) - diferenca)
                break

        print(f"\n----- Valores totais -----\n\nValor total alterado para {valorTotal.text}")
        print(f"Valor total geral alterado para {valorTotalGeral.text}\n")


class Procedimento:
    procedimento: Et.ElementTree

    def __init__(self, procedimento):
        self.setProcedimento(procedimento)

    def setProcedimento(self, procedimento):
        self.procedimento = procedimento

    def getProcedimento(self):
        return self.procedimento

    def alteraCodigoProcedimento(self, guia):
        if len(guia.getListaProcedimento()) > 0:
            codigo = self.getProcedimento().find('ans:procedimento/ans:codigoProcedimento', guia.ans_prefix)
            codigo.text = '0000'
            print("Codigo de procedimento alterado!")

        elif len(guia.getListaDespesa()) > 0:
            codigo = self.getProcedimento().find('.//ans:codigoProcedimento', guia.ans_prefix)
            codigo.text = '00004'
            print("Codigo de procedimento alterado!")

    def alteraValorUnitario(self, guia):
        novoValorUnitario = 10
        valorUnitario = self.getProcedimento().find('.//ans:valorUnitario', guia.ans_prefix)
        quantidadeExecutada = float(self.getProcedimento().find('.//ans:quantidadeExecutada', guia.ans_prefix).text)
        valorTotal = self.getProcedimento().find('.//ans:valorTotal', guia.ans_prefix)
        if float(valorUnitario.text) != novoValorUnitario:
            novoValorTotal = float(novoValorUnitario * quantidadeExecutada)
            if float(valorTotal.text) > novoValorTotal:
                diferenca = (float(valorTotal.text) - novoValorTotal)
            else:
                diferenca = (novoValorTotal - float(valorTotal.text))

            valorUnitario.text = '%.2f' % novoValorUnitario
            valorTotal.text = '%.2f' % novoValorTotal

            print(f"Valor unitario alterado para {valorUnitario.text}")
            print(f"Valor total alterado para {valorTotal.text}")

            guia.alteraValorTotalGeral(diferenca)

    def alteraCodigoTabela(self, guia):
        codigoTabela = self.getProcedimento().find('.//ans:codigoTabela', guia.ans_prefix)
        codigoTabela.text = '050'
        print('Código de tabela alterado para: ' + codigoTabela.text)

    def alteraGrauParticipacao(self, guia):
        grauParticipacao = self.getProcedimento().find('.//ans:grauPart', guia.ans_prefix)
        grauParticipacao.text = '20'
        print('Grau de participação alterado para: ' + grauParticipacao.text)
