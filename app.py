from __future__ import annotations

import contextlib
import json
from pathlib import Path

import streamlit as st
from streamlit_elements import elements, mui

try:
    from streamlit_lottie import st_lottie
except ImportError:  # Fallback if dependency isn't installed yet.
    st_lottie = None


st.set_page_config(page_title="Tic Tac Toe", page_icon="X", layout="centered")

MAX_ROUNDS = 5

LOTTIE_CANDIDATES = (
    "connection-error.json",
    "connectionerror.json",
)

ARENAS = {
    "Arcade Night": {
        "bg": "#0b0f1a",
        "bg_image": "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?auto=format&fit=crop&w=1600&q=80",
        "overlay_1": "rgba(8, 10, 18, 0.82)",
        "overlay_2": "rgba(20, 28, 48, 0.78)",
        "surface": "rgba(18, 23, 34, 0.84)",
        "border": "#38bdf8",
        "text": "#f8fafc",
        "board_text": "#ffffff",
        "muted": "#9aa4b2",
        "accent": "#f472b6",
        "accent_soft": "rgba(244, 114, 182, 0.16)",
        "shadow": "rgba(56, 189, 248, 0.25)",
        "board": "rgba(20, 26, 38, 0.9)",
        "board_hover": "rgba(30, 38, 54, 0.92)",
        "font_url": "https://fonts.googleapis.com/css2?family=VT323&display=swap",
        "font_family": "'VT323', monospace",
        "button_radius": "0px",
        "border_style": "solid",
    },
    "Candy Sky": {
        "bg": "#fff1f2",
        "bg_image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=80",
        "overlay_1": "rgba(255, 214, 214, 0.78)",
        "overlay_2": "rgba(255, 180, 160, 0.72)",
        "surface": "rgba(255, 255, 255, 0.88)",
        "border": "#f472b6",
        "text": "#1f2937",
        "board_text": "#000000",
        "muted": "#6b7280",
        "accent": "#ef4444",
        "accent_soft": "rgba(239, 68, 68, 0.14)",
        "shadow": "rgba(244, 114, 182, 0.3)",
        "board": "rgba(255, 255, 255, 0.92)",
        "board_hover": "rgba(255, 246, 246, 0.95)",
        "font_url": "https://fonts.googleapis.com/css2?family=Chewy&display=swap",
        "font_family": "'Chewy', cursive",
        "button_radius": "24px",
        "border_style": "solid",
    },
    "Cosmic Drift": {
        "bg": "#0a1025",
        "bg_image": "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1600&q=80",
        "overlay_1": "rgba(10, 16, 37, 0.78)",
        "overlay_2": "rgba(33, 46, 78, 0.7)",
        "surface": "rgba(15, 20, 36, 0.82)",
        "border": "#818cf8",
        "text": "#e2e8f0",
        "board_text": "#ffffff",
        "muted": "#94a3b8",
        "accent": "#a855f7",
        "accent_soft": "rgba(168, 85, 247, 0.18)",
        "shadow": "rgba(129, 140, 248, 0.2)",
        "board": "rgba(16, 22, 40, 0.9)",
        "board_hover": "rgba(26, 32, 54, 0.92)",
        "font_url": "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap",
        "font_family": "'Orbitron', sans-serif",
        "button_radius": "8px",
        "border_style": "outset",
    },
    "Retro Doodle": {
        "bg": "#fdfbf7",
        "bg_image": "https://www.transparenttextures.com/patterns/notebook.png",
        "overlay_1": "rgba(253, 251, 247, 0.6)",
        "overlay_2": "rgba(253, 251, 247, 0.8)",
        "surface": "rgba(255, 255, 255, 0.9)",
        "border": "#2d2d2d",
        "text": "#1a1a1a",
        "board_text": "#000000",
        "muted": "#5c5c5c",
        "accent": "#e63946",
        "accent_soft": "rgba(230, 57, 70, 0.15)",
        "shadow": "rgba(0, 0, 0, 0.25)",
        "board": "rgba(255, 255, 255, 0.8)",
        "board_hover": "rgba(250, 250, 250, 0.9)",
        "font_url": "https://fonts.googleapis.com/css2?family=Gochi+Hand&display=swap",
        "font_family": "'Gochi Hand', cursive",
        "button_radius": "2px",
        "border_style": "dashed",
    },
    "Chalkboard": {
        "bg": "#2A363B",
        "bg_image": "https://www.transparenttextures.com/patterns/black-board.png",
        "overlay_1": "rgba(42, 54, 59, 0.7)",
        "overlay_2": "rgba(25, 33, 36, 0.8)",
        "surface": "rgba(50, 65, 71, 0.85)",
        "border": "rgba(255, 255, 255, 0.6)",
        "text": "#FDF6E3",
        "board_text": "#ffffff",
        "muted": "#93A1A1",
        "accent": "#E6A756",
        "accent_soft": "rgba(230, 167, 86, 0.2)",
        "shadow": "rgba(0, 0, 0, 0.6)",
        "board": "rgba(50, 65, 71, 0.5)",
        "board_hover": "rgba(60, 78, 85, 0.8)",
        "font_url": "https://fonts.googleapis.com/css2?family=Permanent+Marker&display=swap",
        "font_family": "'Permanent Marker', cursive",
        "button_radius": "0px",
        "border_style": "solid",
    }
}


def init_state() -> None:
    defaults = {
        "screen": "landing",
        "player_x_name": "Player X",
        "player_o_name": "Player O",
        "selected_arena": "Arcade Night",
        "player_x_input": "Player X",
        "player_o_input": "Player O",
        "arena_input": "Arcade Night",
        "setup_error": "",
        "round_flash": "",
        "round_flash_id": 0,
        "match_flash": "",
        "match_flash_id": 0,
        "match_anim_shown": False,
        "show_round_modal": False,
        "show_match_modal": False,
        "input_locked": False,
        "board": [""] * 9,
        "current_player": "X",
        "rounds_played": 0,
        "x_rounds": 0,
        "o_rounds": 0,
        "draw_rounds": 0,
        "round_finished": False,
        "message": "Set the players and arena to begin.",
        "match_over": False,
        "overall_winner": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.selected_arena not in ARENAS:
        st.session_state.selected_arena = next(iter(ARENAS))
    if st.session_state.arena_input not in ARENAS:
        st.session_state.arena_input = st.session_state.selected_arena


def check_winner(board: list[str]) -> str | None:
    win_lines = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    )
    for a, b, c in win_lines:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(cell for cell in board):
        return "Draw"
    return None


def get_player_name(symbol: str) -> str:
    return st.session_state.player_x_name if symbol == "X" else st.session_state.player_o_name


def current_arena() -> dict[str, str]:
    if st.session_state.selected_arena not in ARENAS:
        st.session_state.selected_arena = next(iter(ARENAS))
    return ARENAS[st.session_state.selected_arena]


def sync_arena() -> None:
    if st.session_state.arena_input in ARENAS:
        st.session_state.selected_arena = st.session_state.arena_input


def apply_theme() -> None:
    theme = current_arena()
    font_url = theme.get("font_url", "https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&display=swap")
    font_family = theme.get("font_family", '"Manrope", "Segoe UI", sans-serif')
    button_radius = theme.get("button_radius", "14px")
    border_style = theme.get("border_style", "solid")
    board_text = theme.get("board_text", theme["text"])
    
    st.markdown(
        f"""
        <style>
            @import url('{font_url}');
            :root {{
                --bg: {theme["bg"]};
                --bg-image: url('{theme["bg_image"]}');
                --overlay-1: {theme["overlay_1"]};
                --overlay-2: {theme["overlay_2"]};
                --surface: {theme["surface"]};
                --border: {theme["border"]};
                --text: {theme["text"]};
                --board-text: {board_text};
                --muted: {theme["muted"]};
                --accent: {theme["accent"]};
                --accent-soft: {theme["accent_soft"]};
                --shadow: {theme["shadow"]};
                --board: {theme["board"]};
                --board-hover: {theme["board_hover"]};
                --font-family: {font_family};
                --button-radius: {button_radius};
                --border-style: {border_style};
            }}
            header[data-testid="stHeader"] {{
                display: none;
            }}
            .stApp {{
                background-color: var(--bg);
                background-image:
                    linear-gradient(135deg, var(--overlay-1), var(--overlay-2)),
                    var(--bg-image);
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: var(--text);
                font-family: var(--font-family);
            }}
            h1, h2, h3, h4, h5, h6, p, span, div, input, select, button, .st-emotion-cache-1104idt p, .st-emotion-cache-1wmy9hl p, .st-emotion-cache-16idsys p {{
                font-family: var(--font-family) !important;
            }}
            [data-testid="stAppViewContainer"] > .main {{
                background: transparent;
            }}
            .block-container {{
                max-width: 980px;
                padding-top: 1.8rem;
                padding-bottom: 2rem;
            }}
            .minimal-card {{
                background: var(--surface);
                border: 2px var(--border-style) var(--border);
                border-radius: var(--button-radius);
                padding: 1.2rem 1.4rem;
                box-shadow: 0 8px 24px var(--shadow);
            }}
            .board-shell {{
                background: var(--surface);
                border: 2px var(--border-style) var(--border);
                border-radius: var(--button-radius);
                padding: 0.75rem;
                box-shadow: 0 8px 20px var(--shadow);
            }}
            div[data-testid="stButton"] > button {{
                border-radius: var(--button-radius);
                border: 2px var(--border-style) var(--border) !important;
                background: var(--board) !important;
                color: var(--board-text) !important;
                transition: transform 0.08s ease, background 0.08s ease, box-shadow 0.08s ease;
                box-shadow: 2px 2px 0px var(--shadow) !important;
            }}

            /* MINIMAL GRID DESIGN */
            div[data-testid="stVerticalBlock"]:has(div.tic-tac-toe-grid) {{
                display: grid !important;
                grid-template-columns: repeat(3, 1fr) !important;
                gap: 8px !important;
                background-color: var(--border) !important;
                border: 8px var(--border-style) var(--border) !important;
                border-radius: var(--button-radius) !important;
                padding: 0 !important;
                overflow: hidden !important;
                box-shadow: 0 12px 40px var(--shadow) !important;
                max-width: 500px !important;
                margin: 2rem auto !important;
            }}
            
            /* Hide the marker */
            div[data-testid="stVerticalBlock"]:has(div.tic-tac-toe-grid) > div.element-container:first-child {{
                display: none !important;
            }}

            /* The cell buttons */
            div[data-testid="stVerticalBlock"]:has(div.tic-tac-toe-grid) div[data-testid="stButton"] > button {{
                border: none !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                transform: none !important;
                background: var(--surface) !important;
                aspect-ratio: 1 / 1 !important;
                min-height: auto !important;
                width: 100% !important;
                margin: 0 !important;
            }}

            div[data-testid="stVerticalBlock"]:has(div.tic-tac-toe-grid) div[data-testid="stButton"] > button:hover:not(:disabled) {{
                background: var(--board-hover) !important;
            }}

            div[data-testid="stVerticalBlock"]:has(div.tic-tac-toe-grid) div[data-testid="stButton"] > button:disabled {{
                background: var(--surface) !important;
                opacity: 1 !important;
            }}
            
            /* Target the huge text inside the new grid */
            div[data-testid="stVerticalBlock"]:has(div.tic-tac-toe-grid) div[data-testid="stButton"] > button * {{
                font-size: clamp(4rem, 15vw, 6.5rem) !important;
                font-weight: 900 !important;
                line-height: 1 !important;
                margin: 0 !important;
                padding: 0 !important;
            }}

            /* Control Buttons (Primary) */
            div[data-testid="stButton"] > button[kind="primary"],
            div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {{
                font-size: 1.1rem !important;
                font-weight: 700 !important;
                min-height: 54px !important;
                color: var(--text) !important;
            }}

            div[data-testid="stButton"] > button:disabled,
            div[data-testid="stButton"] > button[disabled] {{
                opacity: 1 !important;
                color: var(--board-text) !important;
                background: var(--board) !important;
                border: 2px var(--border-style) var(--border) !important;
                box-shadow: 1px 1px 0px var(--shadow) !important;
                transform: translate(1px, 1px) !important;
            }}
            
            div[data-testid="stButton"] > button:hover:not(:disabled) {{
                background: var(--board-hover) !important;
                transform: translate(-1px, -1px) !important;
                box-shadow: 4px 4px 0px var(--shadow) !important;
                color: var(--accent) !important;
                border-color: var(--accent) !important;
            }}
            div[data-testid="stButton"] > button:active:not(:disabled) {{
                transform: translate(1px, 1px) !important;
                box-shadow: 0px 0px 0px var(--shadow) !important;
            }}
            
            @media (max-width: 600px) {{
                .block-container {{
                    padding-left: 0.5rem !important;
                    padding-right: 0.5rem !important;
                    padding-top: 1rem !important;
                }}
                
                /* Force the 3x3 game board to stay as a row on mobile */
                div[data-testid="stVerticalBlock"]:has(div.tic-tac-toe-grid) {{
                    gap: 4px !important;
                    border-width: 4px !important;
                    margin: 1rem auto !important;
                }}

                /* Make the Scoreboard (4 columns) a clean 2x2 grid on mobile */
                div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4):last-child) {{
                    flex-direction: row !important;
                    flex-wrap: wrap !important;
                }}
                div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4):last-child) > div[data-testid="column"] {{
                    flex: 0 0 calc(50% - 0.5rem) !important;
                    min-width: calc(50% - 0.5rem) !important;
                }}

                h1 {{ font-size: 1.8rem !important; }}
            }}
            .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
                background: var(--surface) !important;
                border-radius: var(--button-radius);
                border: 2px var(--border-style) var(--border) !important;
                color: var(--text) !important;
            }}
            .stTextInput input:focus, .stSelectbox div[data-baseweb="select"]:focus-within {{
                border-color: var(--accent) !important;
                box-shadow: 0 0 0 1px var(--accent) !important;
            }}
            .stTextInput input::placeholder {{
                color: var(--muted) !important;
            }}
            .flash-banner {{
                margin: 0.75rem 0 0.6rem;
                padding: 0.75rem 1rem;
                border-radius: var(--button-radius);
                border: 2px var(--border-style) var(--border);
                background: var(--surface);
                color: var(--text);
                font-weight: 600;
                animation: fadeIn 0.28s ease-out both;
            }}
            .flash-banner.match {{
                background: var(--accent-soft);
                border-color: var(--accent);
            }}
            div[data-testid="stModal"] > div {{
                background: var(--surface);
                border: 2px var(--border-style) var(--border);
                border-radius: var(--button-radius);
                box-shadow: 0 16px 40px var(--shadow);
            }}
            div[data-testid="stModal"] h2 {{
                color: var(--text);
            }}
            @keyframes fadeIn {{
                0% {{ opacity: 0; transform: translateY(6px); }}
                100% {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hex_to_rgba(color: str) -> list[float]:
    color = color.lstrip("#")
    r = int(color[0:2], 16) / 255
    g = int(color[2:4], 16) / 255
    b = int(color[4:6], 16) / 255
    return [r, g, b, 1]


def build_pulse_lottie(color: list[float]) -> dict:
    return {
        "v": "5.9.6",
        "fr": 30,
        "ip": 0,
        "op": 60,
        "w": 200,
        "h": 200,
        "nm": "Pulse",
        "ddd": 0,
        "assets": [],
        "layers": [
            {
                "ddd": 0,
                "ind": 1,
                "ty": 4,
                "nm": "Pulse",
                "sr": 1,
                "ks": {
                    "o": {
                        "a": 1,
                        "k": [
                            {"t": 0, "s": [0]},
                            {"t": 10, "s": [100]},
                            {"t": 50, "s": [100]},
                            {"t": 60, "s": [0]},
                        ],
                    },
                    "r": {"a": 0, "k": 0},
                    "p": {"a": 0, "k": [100, 100, 0]},
                    "a": {"a": 0, "k": [0, 0, 0]},
                    "s": {
                        "a": 1,
                        "k": [
                            {"t": 0, "s": [50, 50, 100]},
                            {"t": 30, "s": [100, 100, 100]},
                            {"t": 60, "s": [50, 50, 100]},
                        ],
                    },
                },
                "shapes": [
                    {"ty": "el", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [140, 140]}, "nm": "Ellipse"},
                    {"ty": "fl", "c": {"a": 0, "k": color}, "o": {"a": 0, "k": 100}, "r": 1, "nm": "Fill"},
                    {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}},
                ],
                "ip": 0,
                "op": 60,
                "st": 0,
                "bm": 0,
            }
        ],
    }


def load_lottie_animation() -> dict | None:
    base_dir = Path(__file__).resolve().parent
    for name in LOTTIE_CANDIDATES:
        path = base_dir / name
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as handle:
                    return json.load(handle)
            except (OSError, json.JSONDecodeError):
                return None
    return None


def reset_round() -> None:
    st.session_state.board = [""] * 9
    st.session_state.current_player = "X"
    st.session_state.round_finished = False
    st.session_state.message = f"Round {st.session_state.rounds_played + 1} begins. {get_player_name('X')} starts."


def finish_match() -> None:
    st.session_state.match_over = True
    if st.session_state.x_rounds > st.session_state.o_rounds:
        st.session_state.overall_winner = f"{st.session_state.player_x_name} wins the match."
    elif st.session_state.o_rounds > st.session_state.x_rounds:
        st.session_state.overall_winner = f"{st.session_state.player_o_name} wins the match."
    else:
        st.session_state.overall_winner = "The match ends in a draw."
    st.session_state.message = st.session_state.overall_winner
    st.session_state.match_flash = st.session_state.overall_winner
    st.session_state.match_flash_id += 1
    st.session_state.match_anim_shown = False
    st.session_state.show_round_modal = False
    st.session_state.show_match_modal = True
    st.session_state.input_locked = True


def end_round(result: str) -> None:
    st.session_state.round_finished = True
    st.session_state.rounds_played += 1

    if result == "X":
        st.session_state.x_rounds += 1
        st.session_state.message = f"{st.session_state.player_x_name} wins round {st.session_state.rounds_played}."
    elif result == "O":
        st.session_state.o_rounds += 1
        st.session_state.message = f"{st.session_state.player_o_name} wins round {st.session_state.rounds_played}."
    else:
        st.session_state.draw_rounds += 1
        st.session_state.message = f"Round {st.session_state.rounds_played} ends in a draw."

    st.session_state.round_flash = st.session_state.message
    st.session_state.round_flash_id += 1

    if st.session_state.rounds_played >= MAX_ROUNDS:
        finish_match()
    else:
        reset_round()
        st.session_state.show_round_modal = True
        st.session_state.input_locked = True


def handle_move(index: int) -> None:
    if st.session_state.match_over or st.session_state.round_finished:
        return
    if st.session_state.input_locked:
        return
    if st.session_state.board[index]:
        return
    if st.session_state.round_flash and not st.session_state.match_over:
        st.session_state.round_flash = ""

    st.session_state.board[index] = st.session_state.current_player
    result = check_winner(st.session_state.board)

    if result:
        end_round(result)
        return

    st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"
    st.session_state.message = f"{get_player_name(st.session_state.current_player)}'s turn."


def start_match() -> None:
    name_x = st.session_state.player_x_input.strip() or "Player X"
    name_o = st.session_state.player_o_input.strip() or "Player O"

    if name_x == name_o:
        st.session_state.setup_error = "Choose two different player names."
        return

    st.session_state.player_x_name = name_x
    st.session_state.player_o_name = name_o
    st.session_state.selected_arena = st.session_state.arena_input
    st.session_state.screen = "game"
    st.session_state.setup_error = ""
    restart_match(preserve_theme=True)


def restart_match(preserve_theme: bool = False) -> None:
    selected_arena = st.session_state.selected_arena if preserve_theme else next(iter(ARENAS))
    st.session_state.board = [""] * 9
    st.session_state.current_player = "X"
    st.session_state.rounds_played = 0
    st.session_state.x_rounds = 0
    st.session_state.o_rounds = 0
    st.session_state.draw_rounds = 0
    st.session_state.round_finished = False
    st.session_state.match_over = False
    st.session_state.overall_winner = ""
    st.session_state.round_flash = ""
    st.session_state.match_flash = ""
    st.session_state.match_anim_shown = False
    st.session_state.show_round_modal = False
    st.session_state.show_match_modal = False
    st.session_state.input_locked = False
    st.session_state.selected_arena = selected_arena
    st.session_state.message = f"{st.session_state.player_x_name} starts the match."


def render_win_animation(message: str, anim_key: str, size: int = 160) -> None:
    theme = current_arena()
    if st_lottie:
        lottie_data = load_lottie_animation() or build_pulse_lottie(hex_to_rgba(theme["accent"]))
        st_lottie(
            lottie_data,
            height=size,
            width=size,
            loop=False,
            key=anim_key,
        )
    st.markdown(f"**{message}**")


@contextlib.contextmanager
def modal_context(title: str):
    modal_fn = getattr(st, "modal", None)
    if callable(modal_fn):
        try:
            cm = modal_fn(title)
            if hasattr(cm, "__enter__"):
                with cm:
                    yield
                return
        except Exception:
            pass
    container = st.container()
    with container:
        st.markdown(f"### {title}")
        yield


def render_header() -> None:
    theme = current_arena()
    border_style = theme.get("border_style", "solid")
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 4px 18px; border-bottom: 2px {border_style} {theme['border']}; margin-bottom: 1rem;">
            <div>
                <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: {theme['text']};">Tic Tac Toe</h1>
                <div style="color: {theme['muted']}; font-size: 0.95rem;">Five-round match mode</div>
            </div>
            <div style="border: 2px {border_style} {theme['border']}; padding: 6px 14px; border-radius: 16px; color: {theme['muted']}; font-size: 0.85rem; font-weight: 600;">
                {st.session_state.selected_arena}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scoreboard() -> None:
    theme = current_arena()
    cards = [
        ("Rounds", f"{st.session_state.rounds_played}/{MAX_ROUNDS}"),
        (st.session_state.player_x_name, str(st.session_state.x_rounds)),
        (st.session_state.player_o_name, str(st.session_state.o_rounds)),
        ("Draws", str(st.session_state.draw_rounds)),
    ]
    cols = st.columns(4)
    border_style = theme.get("border_style", "solid")
    button_radius = theme.get("button_radius", "14px")
    for i, (label, value) in enumerate(cards):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background: {theme['surface']}; border: 2px {border_style} {theme['border']}; border-radius: {button_radius}; padding: 14px 16px; text-align: center; box-shadow: 2px 2px 0px {theme['shadow']};">
                    <div style="color: {theme['muted']}; font-size: 0.75rem; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 4px;">{label}</div>
                    <div style="font-weight: 700; color: {theme['text']}; font-size: 1.5rem;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def setup_screen() -> None:
    theme = current_arena()
    st.markdown('<div class="minimal-card">', unsafe_allow_html=True)
    st.markdown("## Match setup")
    st.caption("Choose players and a visual style. The rules stay the same.")

    left, right = st.columns([1.05, 0.95])
    with left:
        st.text_input(
            "Player X name",
            value=st.session_state.player_x_name,
            placeholder="Enter Player X",
            label_visibility="visible",
            key="player_x_input",
        )
        st.text_input(
            "Player O name",
            value=st.session_state.player_o_name,
            placeholder="Enter Player O",
            label_visibility="visible",
            key="player_o_input",
        )
        st.selectbox(
            "Arena",
            list(ARENAS.keys()),
            index=list(ARENAS.keys()).index(st.session_state.selected_arena)
            if st.session_state.selected_arena in ARENAS
            else 0,
            key="arena_input",
            on_change=sync_arena,
        )
        st.button("Start match", type="primary", use_container_width=True, on_click=start_match)
        if st.session_state.setup_error:
            st.error(st.session_state.setup_error)

    with right:
        st.markdown(
            f"""
            <div style="padding: 1rem; border-radius: 14px; border: 1px solid {theme['border']}; background: {theme['surface']};">
                <div style="color: {theme['muted']}; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em;">Format</div>
                <h4 style="margin: 0.35rem 0 0.6rem; color: {theme['text']};">5 rounds total</h4>
                <p style="margin: 0; color: {theme['muted']};">Round wins decide the match winner.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


def game_screen() -> None:
    theme = current_arena()
    st.markdown('<div class="minimal-card">', unsafe_allow_html=True)
    top_left, top_right = st.columns([1.2, 0.8])
    with top_left:
        st.subheader(f"{st.session_state.player_x_name} vs {st.session_state.player_o_name}")
        st.caption("Complete five rounds. Highest score wins.")
    def go_to_lobby():
        st.session_state.screen = "landing"

    with top_right:
        st.button("Back to lobby", type="primary", use_container_width=True, on_click=go_to_lobby)

    render_scoreboard()

    st.markdown(
        f"""
        <div style="margin: 1rem 0 0.6rem; color: {theme['muted']}; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.75rem;">Live status</div>
        <div style="font-weight: 600; font-size: 1rem; color: {theme['text']};">{st.session_state.message}</div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.show_round_modal and not st.session_state.match_over:
        with modal_context("Round complete"):
            render_win_animation(
                st.session_state.round_flash,
                f"round_modal_{st.session_state.round_flash_id}",
                size=140,
            )
            st.caption("Choose an action to continue.")
            def on_next_round():
                st.session_state.show_round_modal = False
                st.session_state.round_flash = ""
                st.session_state.input_locked = False

            def on_restart_round():
                restart_match(preserve_theme=True)
                st.session_state.input_locked = False

            action_cols = st.columns(2)
            action_cols[0].button("Next round", type="primary", use_container_width=True, key="next_round", on_click=on_next_round)
            action_cols[1].button("Restart match", type="primary", use_container_width=True, key="restart_round", on_click=on_restart_round)

    if st.session_state.show_match_modal and st.session_state.match_over:
        with modal_context("Match complete"):
            render_win_animation(
                st.session_state.match_flash,
                f"match_modal_{st.session_state.match_flash_id}",
                size=180,
            )
            st.caption("Choose an action to continue.")
            def on_new_match():
                restart_match(preserve_theme=True)
                st.session_state.input_locked = False

            def on_back_lobby():
                restart_match(preserve_theme=True)
                st.session_state.screen = "landing"
                st.session_state.input_locked = False

            action_cols = st.columns(2)
            action_cols[0].button("New match", type="primary", use_container_width=True, key="new_match", on_click=on_new_match)
            action_cols[1].button("Back to lobby", type="primary", use_container_width=True, key="back_lobby", on_click=on_back_lobby)

    if st.session_state.match_over:
        st.success(st.session_state.overall_winner)

    st.markdown('<br>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="tic-tac-toe-grid"></div>', unsafe_allow_html=True)
        for index in range(9):
            value = st.session_state.board[index]
            label = value if value else " "
            disabled = bool(value) or st.session_state.match_over or st.session_state.input_locked
            st.button(
                label,
                key=f"cell_{index}",
                disabled=disabled,
                use_container_width=True,
                on_click=handle_move,
                args=(index,),
                type="secondary"
            )
    st.markdown('<br>', unsafe_allow_html=True)

    bottom_left, bottom_right = st.columns([0.7, 1.3])
    with bottom_left:
        st.button("Restart match", type="primary", use_container_width=True, on_click=restart_match, args=(True,))
    with bottom_right:
        if st.session_state.match_over:
            st.caption("Match complete. Restart to play again or go back to the lobby.")
        else:
            st.caption(f"{get_player_name(st.session_state.current_player)} to move.")

    st.markdown('</div>', unsafe_allow_html=True)


init_state()
apply_theme()
render_header()

if st.session_state.screen == "landing":
    setup_screen()
else:
    game_screen()