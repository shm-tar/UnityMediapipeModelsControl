import matplotlib.pyplot as plt

def build_graph(fps, millisec, time_counter, is_mediapipe=True) -> None:
    fig = plt.figure()
    fig.set_dpi(100)
    grid = fig.add_gridspec(2, hspace=0)
    axs = grid.subplots(sharex=True)

    fig.suptitle('Time elapsed and FPS')
    axs[0].plot(time_counter, millisec, 'tab:orange')
    axs[1].plot(time_counter, fps, 'tab:blue')

    axs[0].set(ylabel='FPS')
    axs[1].set(xlabel='Image Frames', ylabel='Time Elapsed, ms')

    for ax in axs:
        ax.label_outer()

    if is_mediapipe:
        plt.savefig('Assets/PythonScripts/diagrams/mediapipe_fps_tcp.png')
    else:
        plt.savefig('Assets/PythonScripts/diagrams/dlib_fps_tcp.png')
