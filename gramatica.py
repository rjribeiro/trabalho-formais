import pprint
from leitor import Leitor
from itertools import combinations
from collections import defaultdict

#todo: documentacao da


class Gramatica():
    def __init__(self, arquivo_gramatica):
        with open(arquivo_gramatica, mode='r', encoding="utf-8") as arquivo:
            dados = Leitor(arquivo)
            self._variaveis = dados.variaveis
            self._terminais = dados.terminais
            self._producoes = dados.producoes
            self._simbolo_inicial = dados.inicial

    @property
    def variaveis(self):
        return self._variaveis

    @property
    def terminais(self):
        return self._terminais

    @property
    def producoes(self):
        return self._producoes

    @property
    def simbolo_inicial(self):
        return self._simbolo_inicial

    def simplifica_gramatica(self):
        """
        Objetivo: simplificar um gramatica livre de contexto
        :return:
        """
        #print("remove_producoes_vazias\n")
        #self.__remove_producoes_vazias()
        #print(self)
        #print("#######################")
        #print("\n\nremove_producoes_unitarais\n")
        #self.__remove_producoes_unitarias()
        #print(self)
        self.chonskfy()
        #print("\n\nremove_variaveis_nao_geradoras\n")
        #self.__remove_variaveis_nao_geradoras()
        #print(self)

    def __remove_producoes_vazias(self):
        """
        Objetivo: Dado um conjunto de producoes de uma glc, remove as producoes vazias diretas e indiretas
        Exemplo: Considere "V" o simbolo de vazio e "T" o simbolo de terminal,
         {(A, ("V",)), (B, ("V",)), (C, ("V",)), (D, ("A","B","C","T"))} ->
            {(D, ("A","B","C","T")), (D, ("A","B","T")), (D, ("A","C","T")), (D, ("B","C","T")),
            (D, ("A", "T")), (D, ("B","T")), (D, ("C","T")), (D, ("T",))}

        :return:
        """
        self.__remove_producoes_vazias_indiretas(self.__pop_producoes_vazias_diretas())

    def __pop_producoes_vazias_diretas(self):
        """
        Objetivo: Remove producoes diretas de producoes vazias e retorna as cabecas destas
        Exemplo: {(A, ("V",)), (B, ("V",)), (C, ("V",)), (D, ("A","B","C","T"))} ->
                    {(D, ("A","B","C","T"))}
        :return: lista de cabecas das producoes excluidas
        :rtype: list
        """
        prod_vazias_dir = set()
        for producao in self._producoes:
            if "V" in producao[1]:
                prod_vazias_dir.add(producao)
        self._producoes.difference_update(prod_vazias_dir)
        return [producao[0] for producao in list(prod_vazias_dir)]

    def __remove_producoes_vazias_indiretas(self, vars_com_prod_vazias_dir):
        """
        Objetivo: Remove producoes indiretas de producoes vazias
        Exemplo: {(D, ("A","B","C","T"))} , ["A","B","C"] ->
                    {(D, ("A","B","C","T")), (D, ("A","B","T")), (D, ("A","C","T")), (D, ("B","C","T")),
                    (D, ("A", "T")), (D, ("B","T")), (D, ("C","T")), (D, ("T",))}
        :param vars_com_prod_vazias_dir: lista de cabecas das producoes com producoes vazias diretas
        :return:
        """
        novas_producoes = []
        for producao in self._producoes:
            combinacoes = self.__get_combinacoes_de_variaveis_com_producao_vazia(producao[1], vars_com_prod_vazias_dir)
            for combinacao in combinacoes:
                if len(combinacao) != len(producao[1]):
                    novas_producoes.append((producao[0], tuple(var for var in producao[1] if var not in combinacao)))
        self._producoes.update(novas_producoes)

    def __get_combinacoes_de_variaveis_com_producao_vazia(self, corpo_da_producao, vars_com_producoes_vazias_dir):
        """
        Objetivo: Dado o corpo de uma producao e lista da variaveis que produzem vazio diretamente, retorna
                    a combinacao da intersecao destes
        Exemplo: ("A","B","C,"D"), ["A", "B", "C"] -> (("A",), ("B",), ("B",), ("A", "B"), ("A", "C"),\
                                                        ("C", "B"), ("A", "B", "C"))
        :param corpo_da_producao: tuple
        :param vars_com_producoes_vazias_dir: list
        :return: combinacao da intersecao entre corpo_da_producao e vars_com_producoes_vazias_dir
        :rtype: tuple
        """
        vars_com_prod_vazias_dir_nesse_corpo = set(corpo_da_producao).intersection(vars_com_producoes_vazias_dir)
        combinacoes = []
        for tamanho in range(len(vars_com_prod_vazias_dir_nesse_corpo)+1):
            combinacoes.extend(tuple(combinations(vars_com_prod_vazias_dir_nesse_corpo, tamanho)))
        return tuple(combinacoes[1:])

    def __encontra_producoes_terminais(self, variavel):
        possiveis_producoes = {producao for producao in self._producoes if producao[0] == variavel}
        producoes_terminais = set()

        for producao in possiveis_producoes:
            palavra = ''
            for simbolo in producao[1]:
                palavra = palavra + simbolo
            if palavra not in self._variaveis:
                producoes_terminais.add(producao)
        return producoes_terminais

    def __remove_producoes_unitarias(self):
        fechos = {variavel: set() for variavel in self._variaveis}

        for variavel in self._variaveis:
            vars_unitarias = set()
            for producao in self._producoes:
                if producao[0] == variavel and len(producao[1]) == 1 and producao[1][0] in self._variaveis:
                    vars_unitarias.add(producao[1][0])
            fechos[variavel] = vars_unitarias

        tamanhos = [len(fechos[variavel]) for variavel in fechos]
        tamanhos_novo = []
        while tamanhos != tamanhos_novo:
            for variavel in self._variaveis:
                for cabeca in fechos:
                    if variavel in fechos[cabeca]:
                        fechos[cabeca] = fechos[cabeca].union(fechos[variavel])
            tamanhos = tamanhos_novo
            tamanhos_novo = [len(fechos[variavel]) for variavel in fechos]

        for cabeca in fechos:
            if cabeca in fechos[cabeca]:
                fechos[cabeca].remove(cabeca)

        p1 = set()
        for variavel in self._variaveis:
            p1 = p1.union(self.__encontra_producoes_terminais(variavel))

        for variavel in fechos:
            for B in fechos[variavel]:
                producoes_terminais = self.__encontra_producoes_terminais(B)
                producoes_terminais = {(variavel, prod[1]) for prod in producoes_terminais}
                p1 = p1.union(producoes_terminais)

        self._producoes = p1

    def chonskfy(self):
        lista_vars = "A B C D E F G H I J L M N O P Q R S T U V X W Y Z".split()
        combinacaoes = combinations(lista_vars, 2)
        lista_vars.extend([''.join(combinacao) for combinacao in combinacaoes])

        vars_disponiveis = [vars for vars in lista_vars
                            if vars not in self._variaveis]

        vars_disponiveis = self.__remove_prods_que_misturam_vars_com_term(vars_disponiveis)
        self.__remove_producoes_maiorq2(vars_disponiveis)

    def __remove_prods_que_misturam_vars_com_term(self, variaveis_disponiveis):

        producoes = list(self._producoes)
        dict_vars_novas = dict()

        for producao in range(len(producoes)):
            tamanho_corpo = len(producoes[producao][1])
            if tamanho_corpo > 1:
                for item_corpo in range(tamanho_corpo):
                    if producoes[producao][1][item_corpo] in self._terminais:
                        producao_substituta = list(producoes[producao][1])
                        nova_variavel = dict_vars_novas.setdefault(producao_substituta[item_corpo],
                                                                  variaveis_disponiveis[0])
                        self._variaveis.update(nova_variavel)
                        producao_substituta[item_corpo] = nova_variavel
                        producoes.append((nova_variavel, producoes[producao][1][item_corpo]))
                        producoes[producao] = (producoes[producao][0], tuple(producao_substituta))
                        if nova_variavel == variaveis_disponiveis[0]:
                            variaveis_disponiveis.pop(0)

        self._producoes = set(producoes)
        return variaveis_disponiveis

    def __remove_producoes_maiorq2(self, vars_disponiveis):
        producoes = list(self._producoes)
        for producao in producoes:
            if len(producao[1]) > 2:
                novas_producoes = self.__separa_producao(producao, vars_disponiveis)
                self._producoes.remove(producao)
                self._producoes.update(novas_producoes)

    def __separa_producao(self, producao, vars_disponiveis):
        producao = [producao[0], list(producao[1])]
        tamanho_producao = len(producao[1])
        novas_producoes = []
        vars_novas = []
        while tamanho_producao > 2:
            vars_novas.clear()
            for index in range(0, tamanho_producao-1, 2):
                novas_producoes.append((vars_disponiveis[0], tuple(producao[1][index:index+2])))
                vars_novas.append(vars_disponiveis[0])
                vars_disponiveis.pop(0)
            if tamanho_producao % 2 == 1:
                vars_novas.append(producao[1][-1])
            self._variaveis.update(vars_novas)
            producao = [producao[0], vars_novas.copy()]
            tamanho_producao = len(producao[1])
        novas_producoes.append((producao[0], tuple(vars_novas)))
        return novas_producoes

    # def __remove_variaveis_nao_geradoras(self):
    #     terminais_absolutos = self.__get_terminais_absolutos()
    #     self._producoes = set([producao for producao in self._producoes
    #                            if all([item in terminais_absolutos for item in producao[1]])])
    #     self._variaveis = set()
    #     for producao in self._producoes:
    #         self._variaveis.add(producao[0])
    #
    # def __get_terminais_absolutos(self):
    #     terminais_absolutos = self._terminais.copy()
    #     tamanho_antigo = len(terminais_absolutos)
    #     while True:
    #         for producao in self.producoes:
    #             if all(item in terminais_absolutos for item in producao[1]):
    #                 terminais_absolutos.add(producao[0])
    #         tamanho_novo = len(terminais_absolutos)
    #         if tamanho_novo == tamanho_antigo:
    #             break
    #         else:
    #             tamanho_antigo = tamanho_novo
    #     return terminais_absolutos

    def __str__(self):
        return '''\nG = (V, T, P, {}), ondse:
        \nConjunto de variáveis: \n\tV = {}
        \nConjunto de símbolos terminais: \n\tT = {}
        \nRegras de produção: \nP = {}
        \nSímbolo inicial: {}'''.format(self._simbolo_inicial, self._variaveis, self._terminais,
                    pprint.pformat(self._producoes), self._simbolo_inicial)


if __name__ == '__main__':
    arquivo = input("Digite o caminho do arquivo: ")
    g = Gramatica(arquivo)
    print(g)
    g.remove_producoes_unitarias()
    print(g)
