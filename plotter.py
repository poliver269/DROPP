import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D


class TrajectoryPlotter:
    def __init__(self, trajectory, interactive=True):
        self.data_trajectory = trajectory
        self.fig = None
        self.axes = None
        self.interactive = interactive
        self.colors = mcolors.TABLEAU_COLORS
        if self.interactive:
            mpl.use('TkAgg')
        else:
            pass

    def original_data_with_timestep_slider(self, min_max=None):
        """
        Creates an interactive plot window, where the plotted data at a timestep can be chosen by a Slider.
        Used as in https://matplotlib.org/stable/gallery/widgets/slider_demo.html
        :param min_max: data range of the data with a min and a max value
        """
        if not self.interactive:
            raise ValueError('Plotter has to be interactive to use this plot.')

        if min_max is None:  # min_max is a list of two elements
            min_max = [0, self.data_trajectory.dim['time_frames']]

        self.fig = plt.figure()
        # self.axes = self.fig.add_subplot(111, projection='3d')
        self.axes = Axes3D(self.fig)

        plt.subplots_adjust(bottom=0.25)
        # noinspection PyTypeChecker
        ax_freq = plt.axes([0.25, 0.1, 0.65, 0.03])
        freq_slider = Slider(
            ax=ax_freq,
            label='Time Step',
            valmin=min_max[0],  # minimun value of range
            valmax=min_max[-1] - 1,  # maximum value of range
            valinit=0,
            valstep=1,  # step between values
            valfmt='%0.0f'
        )
        freq_slider.on_changed(self.update_on_slider_change)
        plt.show()

    def plot_original_data_at(self, timeframe):
        self.fig = plt.figure()
        self.axes = Axes3D(self.fig)
        self.update_on_slider_change(timeframe)

    def update_on_slider_change(self, timeframe):
        if 0 <= timeframe <= self.data_trajectory.traj.n_frames:
            timeframe = int(timeframe)
            if self.data_trajectory.params['carbon_atoms_only']:
                x_coordinates = self.data_trajectory.alpha_coordinates[timeframe][:, 0]
                y_coordinates = self.data_trajectory.alpha_coordinates[timeframe][:, 1]
                z_coordinates = self.data_trajectory.alpha_coordinates[timeframe][:, 2]
            else:
                x_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 0]
                y_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 1]
                z_coordinates = self.data_trajectory.traj.xyz[timeframe][:, 2]
            self.axes.cla()
            self.axes.scatter(x_coordinates, y_coordinates, z_coordinates, c='r', marker='.')
            self.axes.set_xlim([self.data_trajectory.coordinate_mins['x'], self.data_trajectory.coordinate_maxs['x']])
            self.axes.set_ylim([self.data_trajectory.coordinate_mins['y'], self.data_trajectory.coordinate_maxs['y']])
            self.axes.set_zlim([self.data_trajectory.coordinate_mins['z'], self.data_trajectory.coordinate_maxs['z']])
            self.axes.set_xlabel('x-Axis')
            self.axes.set_ylabel('y-Axis')
            self.axes.set_zlabel('z-Axis')
            plt.show()
        else:
            raise IndexError('Timestep does not exist')

    def plot_models(self, model_results, data_elements, plot_type='', plot_tics=False, components=None):
        """
        :param model_results:
        :param data_elements:
        :param plot_type: 'heat_map', 'color_map'
        :param plot_tics: True, False
        :param components: int
        """
        if plot_tics:
            self.fig, self.axes = plt.subplots(components + 1, len(model_results))  # subplots(rows, columns)
            main_axes = self.axes[0]  # axes[row][column]
            if len(model_results) == 1:
                for component_nr in range(components + 1)[1:]:
                    self.plot_time_tics(self.axes[component_nr], model_results[0]['projection'], data_elements,
                                        component=component_nr)
            else:
                for i, result in enumerate(model_results):
                    for component_nr in range(components + 1)[1:]:
                        self.plot_time_tics(self.axes[component_nr][i], result['projection'], data_elements,
                                            component=component_nr)
        else:
            self.fig, self.axes = plt.subplots(1, len(model_results))
            main_axes = self.axes

        if plot_type == 'heat_map':
            if len(model_results) == 1:
                self.plot_transformed_data_heat_map(main_axes, model_results[0], data_elements)
            else:
                for i, result in enumerate(model_results):
                    self.plot_transformed_data_heat_map(main_axes[i], result, data_elements)
        else:
            if len(model_results) == 1:
                self.plot_transformed_data_on_axis(main_axes, model_results[0], data_elements, color_map=plot_type)
            else:
                for i, result in enumerate(model_results):
                    self.plot_transformed_data_on_axis(main_axes[i], result, data_elements, color_map=plot_type)
        plt.show()

    def plot_one_model(self, projection_dict, data_elements):
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.cla()
        for element in data_elements:
            self.axes.scatter(projection_dict['projection'][element][:, 0],
                              projection_dict['projection'][element][:, 1], c='r', marker='.')
        plt.show()

    def plot_transformed_data_on_axis(self, ax, projection_list, data_elements, color_map):
        ax.cla()
        ax.set_title(projection_list.get('title_prefix', '') + str(projection_list['model']))
        ax.set_xlabel('1st component')
        ax.set_ylabel('2nd component')
        data_list = projection_list['projection']
        for index, element in enumerate(data_elements):
            if color_map == 'color_map':
                color_array = np.arange(data_list[element].shape[0])
                c_map = plt.cm.viridis
                im = ax.scatter(data_list[element][:, 0], data_list[element][:, 1], c=color_array,
                                cmap=c_map, marker='.')
                if index == 0:
                    self.fig.colorbar(im, ax=ax)
            else:
                color = list(self.colors.values())[element]
                ax.scatter(data_list[element][:, 0], data_list[element][:, 1], c=color, marker='.')

        self.print_model_properties(ax, projection_list)

    def plot_time_tics(self, ax, projections, data_elements, component):
        ax.cla()
        ax.set_xlabel('Time step')
        ax.set_ylabel('Component {}'.format(component))

        for i in data_elements:
            ax.plot(projections[i][:, component - 1], c=list(self.colors.values())[i])

    def plot_transformed_data_heat_map(self, ax, projection_dict, data_elements):
        ax.cla()
        ax.set_title(str(projection_dict['model']))
        ax.set_xlabel('Component 1')
        ax.set_ylabel('Component 2')
        projections = projection_dict['projection']
        for i in data_elements:
            xi = projections[i][:, 0]
            yi = projections[i][:, 1]
            bins = 50
            z, x, y = np.histogram2d(xi, yi, bins)
            np.seterr(divide='ignore')
            free_energies = -np.log(z, dtype='float')
            np.seterr(divide='warn')
            ax.contourf(free_energies.T, bins, cmap=plt.cm.hot, extent=[x[0], x[-1], y[0], y[-1]])
        self.print_model_properties(ax, projection_dict)

    @staticmethod
    def print_model_properties(ax, projection_dict):
        projections = projection_dict['projection']
        model = projection_dict['model']
        try:
            print(projections[0].shape)
            print('EV:', model.eigenvectors, 'EW:', model.eigenvalues)
            # ax.arrow(0, 0, model.eigenvectors[0, 0], model.eigenvectors[1, 0], color='tab:cyan')  # pyemma
            # ax.arrow(0, 0, model.eigenvectors_[0, 0], model.eigenvectors_[1, 0], color='tab:cyan')  # msm builder
        except AttributeError as e:
            print('{}: {}'.format(e, model))

    def ramachandran_plot(self, phi, psi):
        pass

    def matrix_plot(self, matrix, title_prefix='', as_surface=''):
        c_map = plt.cm.viridis
        if as_surface == '3d_map':
            x_coordinates = np.arange(matrix.shape[0])
            y_coordinates = np.arange(matrix.shape[1])
            x_coordinates, y_coordinates = np.meshgrid(x_coordinates, y_coordinates)
            # z_coordinates = np.sin(matrix)
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

    def plot_gauss2d(self, gauss_fitted, xdata, ydata):
        self.fig, self.axes = plt.subplots(1, 1)
        self.axes.plot(xdata, ydata, 'o', label='data')
        self.axes.plot(xdata, gauss_fitted, '-', label='fit')
        self.axes.legend()
        plt.show()
