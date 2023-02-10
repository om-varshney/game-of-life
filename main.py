import game_of_life

board = game_of_life.Board(
    size=100,
    num_spawn=3000,
    save_path="Animations/100/A_Clash_of_Clans.gol",
    num_ticks=1000
)
board.compute_board_states()
animator = game_of_life.Animator(
    width=600,
    height=600,
    title="Game of Life",
    world=board,
    sleep=0,
    start=0,
    cut=5000,
)
animator.animate()
# stat = game_of_life.StatisticGenerator(
#     animation_path="Animations/30/Free_Will",
#     start=0,
#     cut=None,
#     save_path="Plots/Animations_30_Free_Will"
# )
# stat.plot_statistics()

# A Clash of clans is like the best.
# Gods or killers is like the second best up till now!
# Free Will is worth watching.
