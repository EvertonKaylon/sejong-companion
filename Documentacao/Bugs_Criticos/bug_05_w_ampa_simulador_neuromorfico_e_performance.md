# BUG-05: Instabilidade de Memória por Falta de Teto (`w_ampa` / Neuro-Tip)

- **Severidade**: 🟡 Média
- **Módulo**: `src/views/home_view.py` / Neuro-Tip (Cronobiologia)
- **Componente**: Gerenciamento de Memória & Tokens

---

## 1. Descrição do Problema

Durante a execução do simulador e dos cartões dinâmicos de cronobiologia, registrava-se um aumento progressivo no consumo de CPU e RAM em dispositivos com hardware de desenvolvimento limitado (8GB RAM), levando a micro-pausas na renderização do Flet.

---

## 2. Causa Raiz Técnica

O cálculo de parâmetros dinâmicos de estado sem limitação de teto (`w_ampa` sem valor máximo) e o uso de hardcoded magic numbers para estilos e sombras geravam reacoplamento e recalculos desnecessários da árvore de renderização do Flet a cada atualização de estado.

---

## 3. Solução Aplicada

1. **Centralização de Tokens Únicos**: Definição da classe `Tokens` e `Styles` em [src/theme.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/theme.py) para reaproveitamento de `BORDER_RADIUS`, `CARD_SHADOW` e durações de animação.
2. **Encapsulamento por Horário**: Substituição dos cálculos contínuos por verificação determinística de faixas de horário da máquina (cronobiologia matinal, vespertina, noturna e madrugada).

### Código Antes (Variável Sem Teto / Acoplada):
```python
# Recalculava objetos BoxShadow e estilos a cada render
shadow = ft.BoxShadow(blur_radius=10, color="rgba(0,0,0,0.1)", offset=ft.Offset(0, 4))
```

### Código Depois (Tokenizado e Performático):
```python
# Reaproveita constante estática da classe Styles
shadow = Styles.CARD_SHADOW
```

---

## 4. Regra Preventiva

> [!IMPORTANT]
> Nunca instancie novos objetos `ft.BoxShadow` ou esquemas de cores dentro de loops de renderização. Referencie constantes em `Styles` para economizar alocações de memória.
