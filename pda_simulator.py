"""
  PRÁCTICA #4 — AUTÓMATA DE PILA
  Lenguaje: L = { w^m a^n (i+j) d^n w^-m | n, m >= 0, w = (b+c)* }

  Uso en VSCode:
      python pda_simulator.py
  Se abrirá una ventana gráfica con la animación interactiva.

"""

import matplotlib
matplotlib.use('TkAgg')          # ← backend para ventana nativa en VSCode
                                  #   Si falla, prueba: 'Qt5Agg' o 'WXAgg'

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.widgets import Button, TextBox, Slider
import time

#  CLASE PRINCIPAL: SIMULADOR DEL PDA

class PDASimulator:
    """
    Simula el Autómata de Pila que reconoce:
        L = { w^m a^n (i+j) d^n w^-m | n, m >= 0, w = (b+c)* }
    """

    def simulate(self, input_str: str) -> list:
        steps = []
        stack = []
        n = 0
        m = 0
        idx = 0

        def snap(state, char, msg, accept=None):
            steps.append({
                'state':  state,
                'char':   char,
                'stack':  list(stack),
                'idx':    idx,
                'n':      n,
                'm':      m,
                'msg':    msg,
                'accept': accept,
            })

        snap('Q0', '', 'Inicio. Leer w^m: se esperan símbolos b y/o c.')

        while idx < len(input_str) and input_str[idx] in ('b', 'c'):
            char = input_str[idx]
            stack.append(char)
            m += 1
            idx += 1
            snap('Q0', char,
                 f"Q0 → Apilar '{char}' de w^m. Pila: {list_to_str(stack)}")

        while idx < len(input_str) and input_str[idx] == 'a':
            stack.append('A')
            n += 1
            idx += 1
            snap('Q1', 'a',
                 f"Q1 → Apilar marcador A (representa 'a' #{n}). "
                 f"Pila: {list_to_str(stack)}")

        if idx < len(input_str) and input_str[idx] in ('i', 'j'):
            piv = input_str[idx]
            idx += 1
            snap('Q2', piv,
                 f"Q2 → Pivote '{piv}' detectado. "
                 f"La pila NO cambia. Ahora se verificará d^n y w^-m.")
        else:
            found = f"'{input_str[idx]}'" if idx < len(input_str) else "fin de cadena"
            snap('ERR', input_str[idx] if idx < len(input_str) else 'ε',
                 f"ERROR: Se esperaba pivote 'i' o 'j', "
                 f"pero se encontró {found}.", accept=False)
            return steps

        matched_n = 0
        while idx < len(input_str) and input_str[idx] == 'd':
            if stack and stack[-1] == 'A':
                stack.pop()
                matched_n += 1
                idx += 1
                snap('Q3', 'd',
                     f"Q3 → 'd' desapila marcador A "
                     f"({matched_n}/{n}). Pila: {list_to_str(stack)}")
            else:
                top = stack[-1] if stack else "vacía"
                snap('ERR', 'd',
                     f"ERROR: Se intentó desapilar con 'd' pero el tope "
                     f"de la pila es '{top}' (no un marcador A). "
                     f"Hay más 'd' que 'a'.", accept=False)
                return steps

        if matched_n != n:
            snap('ERR', input_str[idx] if idx < len(input_str) else 'ε',
                 f"ERROR: Se leyeron {n} 'a' pero solo {matched_n} 'd'. "
                 f"Faltan {n - matched_n} 'd'.", accept=False)
            return steps

        matched_m = 0
        while idx < len(input_str):
            char = input_str[idx]
            if not stack:
                snap('ERR', char,
                     f"ERROR: La pila ya está vacía pero quedan caracteres "
                     f"'{input_str[idx:]}' sin consumir.", accept=False)
                return steps
            top = stack[-1]
            if char == top:
                stack.pop()
                matched_m += 1
                idx += 1
                snap('Q4', char,
                     f"Q4 → '{char}' coincide con tope '{top}'. Desapilar. "
                     f"({matched_m}/{m}). Pila: {list_to_str(stack)}")
            else:
                snap('ERR', char,
                     f"ERROR: Se esperaba '{top}' (tope de pila) "
                     f"para w^-m, pero se leyó '{char}'.", accept=False)
                return steps

        if matched_m != m:
            snap('ERR', 'ε',
                 f"ERROR: w^m tenía {m} símbolo(s) pero w^-m solo "
                 f"tiene {matched_m}. Cadena incompleta.", accept=False)
            return steps

        if stack:
            snap('ERR', 'ε',
                 f"ERROR: Entrada consumida pero la pila no está vacía: "
                 f"{list_to_str(stack)}.", accept=False)
        else:
            snap('FINAL', 'ε',
                 "✓ Cadena ACEPTADA: entrada consumida y pila vacía.", accept=True)

        return steps


def list_to_str(stack):
    if not stack:
        return "[ vacía ]"
    return "[ " + " | ".join(stack) + " ] ← tope"



#  COLORES Y POSICIONES

STATE_COLORS = {
    'Q0':    ('#4A90D9', '#E8F4FD', 'Leyendo w^m'),
    'Q1':    ('#27AE60', '#EAF7EF', 'Leyendo a^n'),
    'Q2':    ('#E67E22', '#FEF5EC', 'Pivote (i/j)'),
    'Q3':    ('#8E44AD', '#F5EEF8', 'Verificando d^n'),
    'Q4':    ('#1ABC9C', '#E8FAF5', 'Verificando w^-m'),
    'FINAL': ('#16A085', '#D5F5E3', 'ACEPTADA'),
    'ERR':   ('#E74C3C', '#FDEDEC', 'RECHAZADA'),
}

PDA_POSITIONS = {
    'Q0':    (0.10, 0.50),
    'Q1':    (0.32, 0.50),
    'Q2':    (0.54, 0.50),
    'Q3':    (0.76, 0.50),
    'Q4':    (0.54, 0.15),
    'FINAL': (0.98, 0.50),
    'ERR':   (0.76, 0.15),
}

PDA_TRANSITIONS = [
    ('Q0', 'Q0',    'b,c / push',     0.3),
    ('Q0', 'Q1',    'a / push A',     0.0),
    ('Q0', 'Q2',    'i,j / ε',        0.25),
    ('Q1', 'Q1',    'a / push A',     0.3),
    ('Q1', 'Q2',    'i,j / ε',        0.0),
    ('Q2', 'Q3',    'd / pop A',      0.0),
    ('Q2', 'Q4',    'ε (n=0)',        -0.25),
    ('Q3', 'Q3',    'd / pop A',      0.3),
    ('Q3', 'Q4',    'b,c / pop',      0.0),
    ('Q3', 'FINAL', 'ε (m=0,n=0)',    0.2),
    ('Q4', 'Q4',    'b,c / pop',      -0.3),
    ('Q4', 'FINAL', 'ε / pila vacía', 0.0),
    ('Q3', 'ERR',   'error',         -0.2),
    ('Q4', 'ERR',   'error',          0.2),
]


def draw_full_visualization(fig, step: dict, step_num: int, total: int, input_str: str):
    """Dibuja todos los paneles sobre la figura dada (reutilizable en VSCode)."""
    fig.clf()
    state   = step['state']
    color_main, color_bg, state_label = STATE_COLORS.get(state, ('#555', '#EEE', state))

    fig.patch.set_facecolor('#FAFAFA')
    fig.suptitle(
        f"Autómata de Pila  —  L = {{ wᵐ aⁿ (i+j) dⁿ w⁻ᵐ | n,m ≥ 0, w=(b+c)* }}\n"
        f"Cadena: \"{input_str}\"     Paso {step_num}/{total}",
        fontsize=13, fontweight='bold', color='#2C3E50', y=0.98
    )

    # ── Panel 1: Diagrama de transiciones 
    ax1 = fig.add_axes([0.01, 0.08, 0.48, 0.84])
    ax1.set_xlim(-0.05, 1.12)
    ax1.set_ylim(-0.05, 1.05)
    ax1.axis('off')
    ax1.set_facecolor('#F8F9FA')
    ax1.set_title('Diagrama de transiciones del PDA', fontsize=10, color='#555', pad=6)

    drawn_self_loops = {}
    for (src, dst, label, curve) in PDA_TRANSITIONS:
        xs, ys = PDA_POSITIONS[src]
        xd, yd = PDA_POSITIONS[dst]
        is_active = (state == dst) and (step['char'] != '' or state == 'FINAL')
        edge_color = color_main if is_active else '#CCCCCC'
        lw = 1.8 if is_active else 0.9

        if src == dst:
            key = src
            offset = drawn_self_loops.get(key, 0)
            drawn_self_loops[key] = offset + 1
            loop = mpatches.Arc((xs, ys + 0.13 + offset * 0.07), 0.12, 0.10,
                                 angle=0, theta1=30, theta2=330,
                                 color=edge_color, lw=lw)
            ax1.add_patch(loop)
            ax1.annotate('', xy=(xs + 0.04, ys + 0.13),
                         xytext=(xs - 0.04, ys + 0.13),
                         arrowprops=dict(arrowstyle='->', color=edge_color, lw=lw))
            ax1.text(xs, ys + 0.22 + offset * 0.07, label,
                     ha='center', va='bottom', fontsize=6,
                     color=edge_color, style='italic')
        else:
            ax1.annotate('',
                xy=(xd, yd), xytext=(xs, ys),
                arrowprops=dict(
                    arrowstyle='->', color=edge_color, lw=lw,
                    connectionstyle=f'arc3,rad={curve}'
                )
            )
            mx = (xs + xd) / 2 + curve * (yd - ys) * 0.5
            my = (ys + yd) / 2 - curve * (xd - xs) * 0.5
            ax1.text(mx, my, label, ha='center', va='center', fontsize=6,
                     color=edge_color, style='italic',
                     bbox=dict(boxstyle='round,pad=0.1', fc='#FAFAFA',
                               ec='none', alpha=0.8))

    R = 0.07
    for sname, (sx, sy) in PDA_POSITIONS.items():
        is_current = (sname == state)
        sc, sbg, _ = STATE_COLORS.get(sname, ('#888', '#EEE', ''))
        fc    = sc      if is_current else '#FFFFFF'
        ec    = sc      if is_current else '#CCCCCC'
        lw    = 3.0     if is_current else 1.0
        alpha = 1.0     if is_current else 0.7

        circle = plt.Circle((sx, sy), R, color=fc, ec=ec, linewidth=lw,
                             zorder=5, alpha=alpha)
        ax1.add_patch(circle)
        if sname == 'FINAL':
            circle2 = plt.Circle((sx, sy), R * 0.80, fill=False,
                                  ec=ec, linewidth=lw * 0.6, zorder=6)
            ax1.add_patch(circle2)

        tc = '#FFFFFF' if is_current else '#555555'
        ax1.text(sx, sy + 0.01, sname, ha='center', va='center',
                 fontsize=8, fontweight='bold', color=tc, zorder=7)
        _, _, slabel = STATE_COLORS.get(sname, ('#888', '#EEE', sname))
        ax1.text(sx, sy - R - 0.04, slabel, ha='center', va='top',
                 fontsize=6.5, color=sc if is_current else '#999',
                 fontweight='bold' if is_current else 'normal', zorder=7)
        if sname == 'Q0':
            ax1.annotate('', xy=(sx - R, sy),
                         xytext=(sx - R - 0.09, sy),
                         arrowprops=dict(arrowstyle='->', color='#555', lw=1.5))
            ax1.text(sx - R - 0.10, sy, 'inicio',
                     ha='right', va='center', fontsize=7, color='#555')

    # ── Panel 2: Pila 
    ax2 = fig.add_axes([0.52, 0.08, 0.20, 0.84])
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.5, 12)
    ax2.axis('off')
    ax2.set_facecolor('#F8F9FA')
    ax2.set_title('Pila (Stack)\n← fondo   tope →', fontsize=10, color='#555', pad=6)

    stack  = step['stack']
    cell_h = 0.75

    if not stack:
        ax2.text(0.5, 5.5, 'VACÍA', ha='center', va='center',
                 fontsize=14, color='#BBBBBB', style='italic', fontweight='bold')
        ax2.add_patch(FancyBboxPatch((0.05, 0.2), 0.9, 11,
                                     boxstyle='round,pad=0.02',
                                     fc='#F0F0F0', ec='#DDDDDD', lw=1))
    else:
        ax2.add_patch(FancyBboxPatch((0.05, 0.2), 0.9,
                                     min(len(stack) * cell_h + 0.5, 11),
                                     boxstyle='round,pad=0.02',
                                     fc='#F0F0F0', ec='#DDDDDD', lw=1))
        for i, sym in enumerate(stack):
            y = 0.4 + i * cell_h
            is_top = (i == len(stack) - 1)
            sc2 = '#4A90D9' if sym in ('b', 'c') else '#27AE60'
            fc2 = sc2 if is_top else '#ECF0F1'
            ec2 = sc2
            tc2 = '#FFFFFF' if is_top else '#2C3E50'
            ax2.add_patch(FancyBboxPatch((0.12, y), 0.76, cell_h - 0.08,
                                         boxstyle='round,pad=0.04',
                                         fc=fc2, ec=ec2, lw=1.5 if is_top else 0.8))
            ax2.text(0.50, y + (cell_h - 0.08) / 2, sym,
                     ha='center', va='center',
                     fontsize=13, fontweight='bold', color=tc2)
            if is_top:
                ax2.text(0.93, y + (cell_h - 0.08) / 2, '← tope',
                         ha='left', va='center', fontsize=7, color=sc2)

    ax2.text(0.5, -0.3, f'Tamaño: {len(stack)}', ha='center', fontsize=8, color='#777')

    # ── Panel 3: Cinta de entrada
    ax3 = fig.add_axes([0.74, 0.45, 0.25, 0.47])
    ax3.set_xlim(-0.1, max(len(input_str), 1) + 0.3)
    ax3.set_ylim(-0.8, 2.5)
    ax3.axis('off')
    ax3.set_facecolor('#F8F9FA')
    ax3.set_title('Cinta de entrada', fontsize=10, color='#555', pad=6)

    idx_ptr = step['idx']
    for ci, ch in enumerate(input_str):
        already_read = ci < idx_ptr
        is_current   = ci == idx_ptr
        if is_current:
            fc3, ec3, tc3 = color_main, color_main, '#FFFFFF'
        elif already_read:
            fc3, ec3, tc3 = '#ECF0F1', '#BDC3C7', '#95A5A6'
        else:
            fc3, ec3, tc3 = '#FFFFFF', '#95A5A6', '#2C3E50'

        ax3.add_patch(FancyBboxPatch((ci, 0.6), 0.85, 0.9,
                                     boxstyle='round,pad=0.02',
                                     fc=fc3, ec=ec3, lw=1.8 if is_current else 1.0))
        ax3.text(ci + 0.425, 1.05, ch, ha='center', va='center',
                 fontsize=11, fontweight='bold', color=tc3)
        ax3.text(ci + 0.425, 0.3, str(ci), ha='center', va='center',
                 fontsize=7, color='#AAAAAA')
        if is_current:
            ax3.annotate('', xy=(ci + 0.425, 0.6),
                         xytext=(ci + 0.425, -0.2),
                         arrowprops=dict(arrowstyle='->', color=color_main, lw=2))

    if idx_ptr >= len(input_str) and len(input_str) > 0:
        ax3.text(len(input_str) + 0.1, 1.05, '⊣', ha='left', va='center',
                 fontsize=14, color='#E74C3C')

    # ── Panel 4: Info del paso 
    ax4 = fig.add_axes([0.74, 0.08, 0.25, 0.33])
    ax4.axis('off')
    ax4.set_facecolor(color_bg)
    ax4.add_patch(FancyBboxPatch((0, 0), 1, 1,
                                  boxstyle='round,pad=0.02',
                                  fc=color_bg, ec=color_main, lw=2))
    ax4.text(0.5, 0.88, f'Estado: {state}  —  {state_label}',
             ha='center', va='top', fontsize=10, fontweight='bold',
             color=color_main)
    ax4.axhline(y=0.78, xmin=0.05, xmax=0.95, color=color_main, lw=0.8, alpha=0.5)

    char_disp = f"'{step['char']}'" if step['char'] else 'ε (sin leer)'
    info_lines = [
        f"Leyendo:    {char_disp}",
        f"Contador n: {step['n']}  (a's / d's)",
        f"Contador m: {step['m']}  (símbolos w)",
    ]
    for li, line in enumerate(info_lines):
        ax4.text(0.08, 0.68 - li * 0.16, line,
                 ha='left', va='top', fontsize=9.5, color='#2C3E50',
                 fontfamily='monospace')

    ax4.axhline(y=0.22, xmin=0.05, xmax=0.95, color=color_main, lw=0.8, alpha=0.5)
    msg = step['msg']
    if len(msg) > 48:
        mid = msg.rfind(' ', 0, 48)
        mid = mid if mid > 0 else 48
        msg_lines = [msg[:mid], msg[mid:].strip()]
    else:
        msg_lines = [msg]
    for li, ml in enumerate(msg_lines):
        ax4.text(0.08, 0.18 - li * 0.12, ml,
                 ha='left', va='top', fontsize=8.5,
                 color=color_main, style='italic')

    fig.canvas.draw_idle()

#  INTERFAZ INTERACTIVA CON WIDGETS NATIVOS DE MATPLOTLIB

def launch_simulator():
    """Lanza la interfaz interactiva en una ventana nativa de matplotlib."""

    simulator  = PDASimulator()
    state_store = {
        'steps':    [],
        'input':    'bcaaidbcb',
        'cur':      0,
        'auto_run': False,
    }

    # ── Figura principal 
    fig = plt.figure(figsize=(15, 9.5))
    fig.canvas.manager.set_window_title('Simulador PDA — Autómata de Pila')

    # ── Área de visualización (reservamos la zona inferior para controles) .;;.l
    # Los axes de visualización se dibujan dinámicamente en draw_full_visualization.
    # La franja inferior [y=0 .. 0.10] queda libre para los widgets nativos.

    # ── Widgets nativos 
    # TextBox para la cadena de entrada
    ax_text = fig.add_axes([0.08, 0.06, 0.22, 0.055])
    text_box = TextBox(ax_text, 'Cadena: ', initial='bcaaidbcb',
                       color='#EAF2FF', hovercolor='#D0E8FF')

    # Botones de control
    ax_text = fig.add_axes([0.08, 0.06, 0.22, 0.055])
    ax_sim  = fig.add_axes([0.32, 0.06, 0.09, 0.055])
    ax_prev = fig.add_axes([0.42, 0.06, 0.09, 0.055])
    ax_next = fig.add_axes([0.52, 0.06, 0.09, 0.055])
    ax_auto = fig.add_axes([0.62, 0.06, 0.09, 0.055])

    btn_sim  = Button(ax_sim,  '▶ Simular',  color='#4A90D9', hovercolor='#357ABD')
    btn_prev = Button(ax_prev, '◀ Anterior', color='#ECF0F1', hovercolor='#BDC3C7')
    btn_next = Button(ax_next, 'Siguiente ▶',color='#ECF0F1', hovercolor='#BDC3C7')
    btn_auto = Button(ax_auto, '⏵ Auto',     color='#27AE60', hovercolor='#1E8449')

    for btn in (btn_sim, btn_prev, btn_next, btn_auto):
        btn.label.set_fontsize(9)

    # Slider de velocidad
    ax_speed = fig.add_axes([0.72, 0.06, 0.18, 0.040])
    speed_slider = Slider(ax_speed, 'Vel (s)', 0.1, 2.5,
                          valinit=0.7, valstep=0.1, color='#4A90D9')

    # Etiqueta de paso (texto en la figura)
    step_text = fig.text(0.72, 0.02, 'Paso: —', fontsize=9, color='#555',
                     ha='left', va='center')

    # ── Funciones internas

    def render_current():
        s   = state_store
        cur = s['cur']
        tot = len(s['steps'])
        step_text.set_text(f"Paso: {cur + 1} / {tot}")
        draw_full_visualization(fig, s['steps'][cur], cur + 1, tot, s['input'])

    def on_simulate(event=None):
        cadena = text_box.text.strip()
        state_store['steps']    = simulator.simulate(cadena)
        state_store['input']    = cadena
        state_store['cur']      = 0
        state_store['auto_run'] = False
        render_current()

    def on_prev(event):
        if state_store['cur'] > 0:
            state_store['cur'] -= 1
            render_current()

    def on_next(event):
        total = len(state_store['steps'])
        if state_store['cur'] < total - 1:
            state_store['cur'] += 1
            render_current()

    def on_auto(event):
        """Reproduce todos los pasos automáticamente."""
        total = len(state_store['steps'])
        state_store['auto_run'] = True
        state_store['cur'] = 0
        for _ in range(total):
            if not state_store['auto_run']:
                break
            render_current()
            plt.pause(speed_slider.val)
            if state_store['cur'] < total - 1:
                state_store['cur'] += 1
            else:
                break
        state_store['auto_run'] = False

    # Conectar botones
    btn_sim.on_clicked(on_simulate)
    btn_prev.on_clicked(on_prev)
    btn_next.on_clicked(on_next)
    btn_auto.on_clicked(on_auto)

    # Ejecutar simulación inicial y mostrar ventana
    on_simulate()
    plt.show()

#  PUNTO DE ENTRADA

if __name__ == '__main__':
    launch_simulator()