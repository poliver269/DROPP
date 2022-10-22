import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D

from utils.param_key import *


class MyPlotter:
    def __init__(self, interactive=True):
        self.fig = None
        self.axes = None
        self.interactive = interactive
        self.colors = mcolors.TABLEAU_COLORS

        if self.interactive:
            mpl.use('TkAgg')


class TrajectoryPlotter(MyPlotter):
    def __init__(self, trajectory, interactive=True):
        super().__init__(interactive)
        self.data_trajectory = trajectory

    def plot_trajectory_at(self, timestep: int):
        """
        This function gives the opportunity to plot the trajectory at a specific timeframe.
        :param timestep: int
            Time step value of the trajectory
        """
        self.fig = plt.figure()
        self.axes = Axes3D(self.fig)
        self.update_on_slider_change(timestep)

    def original_data_with_timestep_slider(self, min_max=None):
        """
        Creates an interactive plot window, where the trajectory to plot can can be chosen by a Slider at a specific
        timestep. Used as in https://matplotlib.org/stable/gallery/widgets/slider_demo.html
        :param min_max: data range of the data with a min and a max value
        """
        if not self.interactive:
            raise ValueError('Plotter has to be interactive to use this plot.')

        if min_max is None:  # min_max is a list of two elements
            min_max = [0, self.data_trajectory.dim[TIME_FRAMES]]

        self.fig = plt.figure()
        self.axes = Axes3D(self.fig)

        plt.subplots_adjust(bottom=0.25)
        # noinspection PyTypeChecker
        ax_freq = plt.axes([0.25, 0.1, 0.65, 0.03])
        freq_slider = Slider(
            ax=ax_freq,
            label='Time Step',
            valmin=min_max[0],  # minimum value of range
            valmax=min_max[-1] - 1,  # maximum value of range
            valinit=1,
            valstep=1,  # step between values
            valfmt='%0.0f'
        )
        freq_slider.on_changed(self.update_on_slider_change)
        plt.show()

    def update_on_slider_change(self, timeframe):
        """
        Callable function for the slider, which updates the figure.
        :param timeframe: Input value of the slider.
        :return:
        """
        if 0 <= timeframe <= self.data_trajectory.traj.n_frames:
            timeframe = int(timeframe)
            if self.data_trajectory.params[CARBON_ATOMS_ONLY]:
                x_coordinates = self.data_trajectory.alpha_carbon_coordinates[timeframe][:, 0]
                y_coordinates = self.data_trajectory.alpha_carbon_coordinates[timeframe][:, 1]
                z_coordinates = self.data_trajectory.alpha_carbon_coordinates[timeframe][:, 2]
            else:
                x_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 0]
                y_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 1]
                z_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 2]
            self.axes.cla()
            self.axes.scatter(x_coordinates, y_coordinates, z_coordinates, c='r', marker='.')
            self.axes.set_xlim(self.data_trajectory.coordinate_mins[X], self.data_trajectory.coordinate_maxs[X])
            self.axes.set_ylim(self.data_trajectory.coordinate_mins[Y], self.data_trajectory.coordinate_maxs[Y])
            self.axes.set_zlim(self.data_trajectory.coordinate_mins[Z], self.data_trajectory.coordinate_maxs[Z])
            self.axes.set_xlabel('x-Axis')
            self.axes.set_ylabel('y-Axis')
            self.axes.set_zlabel('z-Axis')
            plt.show()
        else:
            raise IndexError('Timestep does not exist')


class TrajectoryResultPlotter(MyPlotter):
    def plot_models(self, model_results, data_elements, plot_type='', plot_tics=False, components=None):
        """
        Plots the model results in 2d-coordinate system next to each other.
        Alternatively with tics of the components can be plotted under the figures when `plot_tics` is True
        :param model_results: list of dictionary
            dict should contain the keys: 'model', 'projection', 'title_prefix' (optional)
        :param data_elements: List of elements
            The result of the models can contain a list of results,
            from which is possible to choose with this parameter
        :param plot_type: param_key.plot_type
        :param plot_tics: bool (default: False)
            Plots the component tics under the base figures if True
        :param components: int
            Number of components used for the reduced
        """
        if plot_tics:
            self.fig, self.axes = plt.subplots(components + 1, len(model_results))  # subplots(rows, columns)
            main_axes = self.axes[0]  # axes[row][column]
            if len(model_results) == 1:
                for component_nr in range(components + 1)[1:]:
                    self.plot_time_tics(self.axes[component_nr], model_results[0][PROJECTION], data_elements,
                                        component=component_nr)
            else:
                for i, result in enumerate(model_results):
                    for component_nr in range(components + 1)[1:]:
                        self.plot_time_tics(self.axes[component_nr][i], result[PROJECTION], data_elements,
                                            component=component_nr)
        else:
            self.fig, self.axes = plt.subplots(1, len(model_results))
            main_axes = self.axes

        if plot_type == HEAT_MAP:
            if len(model_results) == 1:
                self.plot_transformed_data_heat_map(main_axes, model_results[0], data_elements)
            else:
                for i, result in enumerate(model_results):
                    self.plot_transformed_data_heat_map(main_axes[i], result, data_elements)
        else:
            if len(model_results) == 1:
                self.plot_transformed_trajectory(main_axes, model_results[0], data_elements, color_map=plot_type)
            else:
                for i, result in enumerate(model_results):
                    self.plot_transformed_trajectory(main_axes[i], result, data_elements, color_map=plot_type)
        plt.show()

    def plot_transformed_trajectory(self, ax, projection, data_elements, color_map):
        """
        Plot the projection results of the transformed trajectory on an axis
        :param ax: Which axis the result should be plotted on
        :param projection: dictionary
            dict should contain the keys: 'model', 'projection', 'title_prefix' (optional)
        :param data_elements: List of elements
            The result of the models can contain a list of results,
            from which is possible to choose with this parameter
        :param color_map: str
            String value of the plot mapping type
        """
        ax.cla()
        ax.set_title(projection.get(TITLE_PREFIX, '') + str(projection[MODEL]))
        ax.set_xlabel('1st component')
        ax.set_ylabel('2nd component')
        data_list = projection[PROJECTION]
        for index, element in enumerate(data_elements):
            if color_map == COLOR_MAP:
                color_array = np.arange(data_list[element].shape[0])
                c_map = plt.cm.viridis
                im = ax.scatter(data_list[element][:, 0], data_list[element][:, 1], c=color_array,
                                cmap=c_map, marker='.')
                if index == 0:
                    self.fig.colorbar(im, ax=ax)
            else:
                color = list(self.colors.values())[element]
                ax.scatter(data_list[element][:, 0], data_list[element][:, 1], c=color, marker='.')

        self.print_model_properties(projection)

    def plot_time_tics(self, ax, projections, data_elements, component):
        """
        Plot the time tics on a specific axis
        :param ax: axis
        :param projections:
        :param data_elements: List of elements
            The result of the models can contain a list of results,
            from which is possible to choose with this parameter.
        :param component:
        :return:
        """
        ax.cla()
        ax.set_xlabel('Time step')
        ax.set_ylabel('Component {}'.format(component))

        for i in data_elements:
            ax.plot(projections[i][:, component - 1], c=list(self.colors.values())[i])

    def plot_transformed_data_heat_map(self, ax, projection_dict, data_elements):
        """

        :param ax:
        :param projection_dict:
        :param data_elements: List of elements
            The result of the models can contain a list of results,
            from which is possible to choose with this parameter.
        :return:
        """
        ax.cla()
        ax.set_title(str(projection_dict[MODEL]))
        ax.set_xlabel('Component 1')
        ax.set_ylabel('Component 2')
        projections = projection_dict[PROJECTION]
        for i in data_elements:
            xi = projections[i][:, 0]
            yi = projections[i][:, 1]
            bins = 50
            z, x, y = np.histogram2d(xi, yi, bins)
            np.seterr(divide='ignore')
            free_energies = -np.log(z, dtype='float')
            np.seterr(divide='warn')
            ax.contourf(free_energies.T, bins, cmap=plt.cm.hot, extent=[x[0], x[-1], y[0], y[-1]])
        self.print_model_properties(projection_dict)

    @staticmethod
    def print_model_properties(projection_dict):
        """
        Prints the model result properties: Eigenvector (EV) and Eigenvalue (EW)
        :param projection_dict: dictionary
            dict should contain the keys: 'model', 'projection'
        """
        projections = projection_dict[PROJECTION]
        model = projection_dict[MODEL]
        try:
            print(projections[0].shape)
            print('EV:', model.eigenvectors, 'EW:', model.eigenvalues)
        except AttributeError as e:
            print('{}: {}'.format(e, model))


class ArrayPlotter(MyPlotter):
    def matrix_plot(self, matrix, title_prefix='', as_surface=''):
        """
        Plots the values of a matrix on a 2d or a 3d axes
        :param matrix: ndarray matrix, which should be plotted
        :param title_prefix: str
        :param as_surface: Plot as a 3d-surface if value PLOT_3D_MAP else 2d-axes
        """
        c_map = plt.cm.viridis
        if as_surface == PLOT_3D_MAP:
            x_coordinates = np.arange(matrix.shape[0])
            y_coordinates = np.arange(matrix.shape[1])
            x_coordinates, y_coordinates = np.meshgrid(x_coordinates, y_coordinates)
            self.fig = plt.figure()
            self.axes = self.fig.gca(projection='3d')
            im = self.axes.plot_surface(x_coordinates, y_coordinates, matrix, cmap=c_map)
        else:
            self.fig, self.axes = plt.subplots(1, 1)
            im = self.axes.matshow(matrix, cmap=c_map)
        self.fig.colorbar(im, ax=self.axes)
        self.axes.set_xlabel('atoms')
        self.axes.set_ylabel('time series')
        self.axes.set_title(title_prefix + ' Matrix')
        plt.show()

    def plot_gauss2d(self, gauss_fitted, xdata, ydata, title_prefix='', mean_data=None):
        """
        Plot the data (ydata) in a range (xdata), the (fitted) gauss curve and a line (mean, median)
        :param gauss_fitted: A curve
        :param xdata: range of plotting
        :param ydata:
        :param title_prefix:
        :param mean_data:
        :return:
        """
        self.fig, self.axes = plt.subplots(1, 1)
        self.axes.plot(xdata, ydata, 'o', label='data')
        self.axes.plot(xdata, gauss_fitted, '-', label='fit')
        if mean_data is not None:
            self.axes.plot(xdata, mean_data, '-', label='mean')
        self.axes.legend()
        self.axes.set_title(title_prefix)
        # self.axes.set_ylim(-1, 1)
        plt.show()
