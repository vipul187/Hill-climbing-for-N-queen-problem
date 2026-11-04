
import streamlit as st
import matplotlib.pyplot as plt
import random
import time

st.set_page_config(page_title="N-Queen Hill Climbing", layout="wide")

st.title("♛ N-Queen Problem")
st.subheader("Steepest-Ascent Hill Climbing with Random Restarts")

st.write("Visualize how the Hill Climbing algorithm solves the N-Queen problem.")

n = st.sidebar.slider("Number of Queens (N)", 4, 12, 8)
speed = st.sidebar.slider("Animation Speed", 0.05, 1.0, 0.3)

def heuristic(board):
    h = 0
    for i in range(len(board)):
        for j in range(i + 1, len(board)):
            if board[i] == board[j] or abs(board[i] - board[j]) == j - i:
                h += 1
    return h

def draw_board(board, placeholder, moves, restarts):
    fig, ax = plt.subplots(figsize=(6, 6))

    for r in range(len(board)):
        for c in range(len(board)):
            color = "#5aa786" if (r+c) % 2 == 0 else "#f1dfb6"
            ax.add_patch(plt.Rectangle(
                (c, r), 1, 1, facecolor=color
            ))

    for c, r in enumerate(board):
        ax.text(c + 0.5, n - r - 0.5, "♛",
                ha="center", va="center", fontsize=30)

    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")

    placeholder.pyplot(fig)
    plt.close(fig)

    st.caption(
        f"Attacking pairs: {heuristic(board)} | "
        f"Moves: {moves} | Restarts: {restarts}"
    )

def solve():
    board = [random.randrange(n) for _ in range(n)]
    moves = 0
    restarts = 0

    board_area = st.empty()
    status = st.empty()

    for iteration in range(3000):
        h = heuristic(board)

        draw_board(board, board_area, moves, restarts)

        if h == 0:
            status.success("Solution found! No queens attack each other.")
            return

        best = h
        options = []

        for c in range(n):
            original = board[c]

            for r in range(n):
                if r == original:
                    continue

                board[c] = r
                score = heuristic(board)

                if score < best:
                    best = score
                    options = [(c, r)]
                elif score == best and score < h:
                    options.append((c, r))

            board[c] = original

        if best >= h:
            restarts += 1
            board = [random.randrange(n) for _ in range(n)]
            status.warning("Local minimum reached. Random restart!")
        else:
            c, r = random.choice(options)
            board[c] = r
            moves += 1
            status.info(f"Improving solution... Current heuristic: {best}")

        time.sleep(speed)

    status.error("Maximum iterations reached. Try running again.")

if st.button("▶ Run Animation", type="primary"):
    solve()

