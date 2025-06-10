#!/usr/bin/env python3
"""
Sistema de gerenciamento de avatares para reels
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class GerenciadorAvatares:
    """Classe para gerenciar múltiplos avatares e sua rotação"""
    
    def __init__(self):
        self.config_path = "config/avatares_sistema.json"
        self.config = self._carregar_config()
    
    def _carregar_config(self) -> Dict:
        """Carrega configuração dos avatares"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Configuração padrão se arquivo não existir
            return {
                "avatares_disponiveis": [],
                "configuracao_rotacao": {
                    "modo_rotacao": "sequencial",
                    "proximo_avatar_index": 0,
                    "historico_ultimos_usos": []
                },
                "estatisticas": {
                    "total_reels_gerados": 0,
                    "avatar_mais_usado": None,
                    "criado_em": datetime.now().strftime("%Y-%m-%d"),
                    "atualizado_em": datetime.now().strftime("%Y-%m-%d")
                }
            }
    
    def _salvar_config(self):
        """Salva configuração no arquivo"""
        self.config["estatisticas"]["atualizado_em"] = datetime.now().strftime("%Y-%m-%d")
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def adicionar_avatar(self, avatar_id: str, nome: str, descricao: str = ""):
        """Adiciona novo avatar ao sistema"""
        
        # Verificar se já existe
        for avatar in self.config["avatares_disponiveis"]:
            if avatar["id"] == avatar_id:
                print(f"⚠️ Avatar {avatar_id} já existe!")
                return False
        
        # Adicionar novo avatar
        novo_avatar = {
            "id": avatar_id,
            "nome": nome,
            "descricao": descricao,
            "status": "ativo",
            "ultimo_uso": None,
            "total_usos": 0
        }
        
        self.config["avatares_disponiveis"].append(novo_avatar)
        self._salvar_config()
        
        print(f"✅ Avatar adicionado: {nome} ({avatar_id})")
        return True
    
    def listar_avatares(self):
        """Lista todos os avatares disponíveis"""
        print("📋 AVATARES DISPONÍVEIS:")
        print("=" * 50)
        
        if not self.config["avatares_disponiveis"]:
            print("❌ Nenhum avatar cadastrado")
            return
        
        for i, avatar in enumerate(self.config["avatares_disponiveis"], 1):
            status_emoji = "✅" if avatar["status"] == "ativo" else "❌"
            ultimo_uso = avatar["ultimo_uso"] or "Nunca"
            
            print(f"{i}. {status_emoji} {avatar['nome']}")
            print(f"   ID: {avatar['id']}")
            print(f"   Descrição: {avatar['descricao']}")
            print(f"   Último uso: {ultimo_uso}")
            print(f"   Total de usos: {avatar['total_usos']}")
            print()
    
    def obter_proximo_avatar(self) -> Optional[str]:
        """Obtém o próximo avatar na rotação"""
        avatares_ativos = [a for a in self.config["avatares_disponiveis"] if a["status"] == "ativo"]
        
        if not avatares_ativos:
            print("❌ Nenhum avatar ativo disponível!")
            return None
        
        # Rotação sequencial
        index_atual = self.config["configuracao_rotacao"]["proximo_avatar_index"]
        
        # Garantir que o índice está dentro do range
        if index_atual >= len(avatares_ativos):
            index_atual = 0
        
        avatar_escolhido = avatares_ativos[index_atual]
        
        # Atualizar para próximo
        proximo_index = (index_atual + 1) % len(avatares_ativos)
        self.config["configuracao_rotacao"]["proximo_avatar_index"] = proximo_index
        
        # Registrar uso
        self._registrar_uso_avatar(avatar_escolhido["id"])
        
        print(f"🎭 Avatar selecionado: {avatar_escolhido['nome']} ({avatar_escolhido['id']})")
        return avatar_escolhido["id"]
    
    def _registrar_uso_avatar(self, avatar_id: str):
        """Registra uso de um avatar"""
        hoje = datetime.now().strftime("%Y-%m-%d")
        
        # Atualizar avatar específico
        for avatar in self.config["avatares_disponiveis"]:
            if avatar["id"] == avatar_id:
                avatar["ultimo_uso"] = hoje
                avatar["total_usos"] += 1
                break
        
        # Atualizar estatísticas gerais
        self.config["estatisticas"]["total_reels_gerados"] += 1
        
        # Atualizar avatar mais usado
        avatar_mais_usado = max(
            self.config["avatares_disponiveis"],
            key=lambda x: x["total_usos"]
        )
        self.config["estatisticas"]["avatar_mais_usado"] = avatar_mais_usado["id"]
        
        # Adicionar ao histórico
        self.config["configuracao_rotacao"]["historico_ultimos_usos"].append({
            "avatar_id": avatar_id,
            "data": hoje
        })
        
        # Manter apenas últimos 10 usos no histórico
        if len(self.config["configuracao_rotacao"]["historico_ultimos_usos"]) > 10:
            self.config["configuracao_rotacao"]["historico_ultimos_usos"] = \
                self.config["configuracao_rotacao"]["historico_ultimos_usos"][-10:]
        
        self._salvar_config()
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas de uso dos avatares"""
        print("📊 ESTATÍSTICAS DOS AVATARES")
        print("=" * 40)
        
        stats = self.config["estatisticas"]
        print(f"📈 Total de reels gerados: {stats['total_reels_gerados']}")
        print(f"🎭 Total de avatares: {len(self.config['avatares_disponiveis'])}")
        
        if stats["avatar_mais_usado"]:
            avatar_top = next(
                (a for a in self.config["avatares_disponiveis"] 
                 if a["id"] == stats["avatar_mais_usado"]), None
            )
            if avatar_top:
                print(f"🏆 Avatar mais usado: {avatar_top['nome']} ({avatar_top['total_usos']} usos)")
        
        print(f"📅 Sistema criado em: {stats['criado_em']}")
        print(f"🔄 Última atualização: {stats['atualizado_em']}")
        
        # Histórico recente
        historico = self.config["configuracao_rotacao"]["historico_ultimos_usos"]
        if historico:
            print(f"\n📋 Últimos {len(historico)} usos:")
            for uso in historico[-5:]:  # Mostrar últimos 5
                avatar = next(
                    (a for a in self.config["avatares_disponiveis"] 
                     if a["id"] == uso["avatar_id"]), None
                )
                nome = avatar["nome"] if avatar else "Avatar removido"
                print(f"  • {uso['data']}: {nome}")
    
    def remover_avatar(self, avatar_id: str):
        """Remove avatar do sistema"""
        for i, avatar in enumerate(self.config["avatares_disponiveis"]):
            if avatar["id"] == avatar_id:
                nome = avatar["nome"]
                del self.config["avatares_disponiveis"][i]
                self._salvar_config()
                print(f"✅ Avatar removido: {nome}")
                return True
        
        print(f"❌ Avatar {avatar_id} não encontrado")
        return False


def menu_interativo():
    """Menu interativo para gerenciar avatares"""
    gerenciador = GerenciadorAvatares()
    
    while True:
        print("\n🎭 GERENCIADOR DE AVATARES")
        print("=" * 30)
        print("1. Listar avatares")
        print("2. Adicionar avatar")
        print("3. Obter próximo avatar") 
        print("4. Mostrar estatísticas")
        print("5. Remover avatar")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            gerenciador.listar_avatares()
        
        elif opcao == "2":
            avatar_id = input("ID do avatar: ").strip()
            nome = input("Nome do avatar: ").strip()
            descricao = input("Descrição (opcional): ").strip()
            gerenciador.adicionar_avatar(avatar_id, nome, descricao)
        
        elif opcao == "3":
            avatar_id = gerenciador.obter_proximo_avatar()
            if avatar_id:
                print(f"Use este ID no seu script: {avatar_id}")
        
        elif opcao == "4":
            gerenciador.mostrar_estatisticas()
        
        elif opcao == "5":
            avatar_id = input("ID do avatar para remover: ").strip()
            gerenciador.remover_avatar(avatar_id)
        
        elif opcao == "0":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")


if __name__ == "__main__":
    print("🎭 SISTEMA DE GERENCIAMENTO DE AVATARES")
    print("Adicione os IDs dos seus novos avatares aqui!")
    print("O sistema irá rotacionar automaticamente a cada reel.")
    print()
    
    # Mostrar avatares atuais
    gerenciador = GerenciadorAvatares()
    gerenciador.listar_avatares()
    
    menu_interativo()