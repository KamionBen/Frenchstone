import numpy as np
import random
import pickle
import matplotlib.pyplot as plt
from tf_agents.trajectories import time_step as ts
import tensorflow as tf
from tf_agents.agents.dqn import dqn_agent
from tf_agents.specs import array_spec
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.environments import py_environment, tf_py_environment
from tf_agents.networks import sequential
from tf_agents.policies import random_tf_policy, q_policy, PolicySaver
from tf_agents.trajectories import trajectory
from tf_agents.specs import tensor_spec
from tf_agents.utils import common
from sklearn.model_selection import train_test_split
from tf_agents.utils.nest_utils import unbatch_nested_tensors




""" Chargement des données d'entraînement et de données d'init """
with open('logs_refined.pickle', 'rb') as f:
    df_state = pickle.load(f)

dict_actions = {
  0: "passer_tour",
  1: "jouer_carte",
  2: "attaquer"
}
class Frenchstone(py_environment.PyEnvironment):
    def __init__(self, data):
        self.data = data
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=2, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(shape=(1, self.data.shape[1]), dtype=np.int32, minimum=-100, maximum=100, name='observation')
        self._state = self.data.loc[random.randint(0, self.data.shape[0] - 1)]
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self._state = self.data.loc[random.randint(0, self.data.shape[0] - 1)]
        self._episode_ended = False
        return ts.restart(np.array([self._state], dtype=np.int32))

    def _step(self, action):


        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        self._state = self.data.loc[random.randint(0, self.data.shape[0] - 1)]

        legal_actions = [0]
        """ Calcul de la récompense """
        """ Ici, on doit déterminer les actions légales en fonction de l'état tiré au hasard """
        """ Peut-on jouer une carte ? """
        for i in range(int(self._state["nbre_cartes_j"])):
            if self._state[f"carte_en_main{i + 1}_cost"] <= self._state["mana_dispo_j"] and self._state[f"carte_en_main{i + 1}_cost"] != 99:
                legal_actions.append(1)
                break
        """ Peut-on attaquer ? """
        for i in range(7):
            if self._state[f"atq_remain_serv{i + 1}_j"] > 0:
                legal_actions.append(2)
                break

        if int(action) not in legal_actions:
            reward = -100
            self._episode_ended = True
            return ts.termination(np.array([self._state], dtype=np.int32), reward)
        if len(legal_actions) == 1:
            reward = 0
            self._episode_ended = True
            return ts.termination(np.array([self._state], dtype=np.int32), reward)
        else:
            if int(action) == self._state['action']:
                if self._state['victoire'] == 1:
                    reward = 1
                else:
                    reward = -1
                if int(action) == 0:
                    self._episode_ended = True
                    return ts.termination(np.array([self._state], dtype=np.int32), reward)
                else:
                    return ts.transition(np.array([self._state], dtype=np.int32), reward)
            else:
                if self._state['victoire'] == 1:
                    reward = -0.05
                else:
                    reward = 0.05
                if int(action) == 0:
                    self._episode_ended = True
                    return ts.termination(np.array([self._state], dtype=np.int32), reward)
                else:
                    return ts.transition(np.array([self._state], dtype=np.int32), reward)



X_train, X_test = train_test_split(df_state, test_size=0.2)
train_env = Frenchstone(X_train.reset_index().drop('index', axis=1))
eval_env = Frenchstone(X_test.reset_index().drop('index', axis=1))
train_env = tf_py_environment.TFPyEnvironment(train_env)
eval_env = tf_py_environment.TFPyEnvironment(eval_env)
time_step = train_env.reset()

num_iterations = 500000  # @param {type:"integer"}
initial_collect_steps = 10  # @param {type:"integer"}
collect_steps_per_iteration = 1  # @param {type:"integer"}
replay_buffer_max_length = 100000  # @param {type:"integer"}

batch_size = 512  # @param {type:"integer"}
learning_rate = 1e-4  # @param {type:"number"}
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=1e-4,
    decay_steps=10000,
    decay_rate=0.95)
log_interval = 500  # @param {type:"integer"}

num_eval_episodes = 100  # @param {type:"integer"}
eval_interval = 1000  # @param {type:"integer"}

replay_buffer_capacity = 100000  # @param {type:"integer"}

fc_layer_params = (300, 150, 100, 32, 16)
action_tensor_spec = tensor_spec.from_spec(train_env.action_spec())
num_actions = action_tensor_spec.maximum - action_tensor_spec.minimum + 1


# Define a helper function to create Dense layers configured with the right
# activation and kernel initializer.
def dense_layer(num_units):
    return tf.keras.layers.Dense(
      num_units,
      activation=tf.keras.activations.relu,
      kernel_initializer=tf.keras.initializers.VarianceScaling(
          scale=2.0, mode='fan_in', distribution='truncated_normal'))


# QNetwork consists of a sequence of Dense layers followed by a dense layer
# with `num_actions` units to generate one q_value per available action as
# its output.
mask_layer = tf.keras.layers.Masking(mask_value=-99)
dense_layers = [dense_layer(num_units) for num_units in fc_layer_params]
q_values_layer = tf.keras.layers.Dense(
    num_actions,
    activation=None,
    kernel_initializer=tf.keras.initializers.RandomUniform(
        minval=-0.03, maxval=0.03),
    bias_initializer=tf.keras.initializers.Constant(-0.2))
flatten_layer = tf.keras.layers.Flatten()
q_net = sequential.Sequential(dense_layers + [q_values_layer] + [flatten_layer])

optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)

train_step_counter = tf.Variable(0)


# def observation_action_splitter(obs):
#     return obs['observations'], obs['valid_actions']


agent = dqn_agent.DqnAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=common.element_wise_squared_loss,
    train_step_counter=train_step_counter,
    epsilon_greedy=0.33)

agent.initialize()

def compute_avg_return(environment, policy, num_episodes=10):
    total_return = 0.0
    for _ in range(num_episodes):
        time_step = environment.reset()
        episode_return = 0.0

        while not time_step.is_last():
            action_step = policy.action(time_step)
            time_step = environment.step(action_step.action)
            episode_return += time_step.reward
        total_return += episode_return

    avg_return = total_return / num_episodes
    return avg_return.numpy()[0]


random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(),
                                                train_env.action_spec())

q_policy = q_policy.QPolicy(train_env.time_step_spec(),
                            train_env.action_spec(),
                            q_net)

compute_avg_return(eval_env, q_policy, num_eval_episodes)



# @test {"skip": true}
replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=train_env.batch_size,
    max_length=replay_buffer_capacity)

print(replay_buffer.data_spec)
def collect_step(environment, policy):
    time_step = environment.current_time_step()
    action_step = policy.action(time_step)
    next_time_step = environment.step(action_step.action)
    traj = trajectory.from_transition(time_step, action_step, next_time_step)
    print(traj)

    # Add trajectory to the replay buffer
    replay_buffer.add_batch(traj)


for _ in range(initial_collect_steps):
    collect_step(train_env, q_policy)

# This loop is so common in RL, that we provide standard implementations of
# these. For more details see the drivers module.

# Dataset generates trajectories with shape [BxTx...] where
# T = n_step_update + 1.
dataset = replay_buffer.as_dataset(
    num_parallel_calls=3, sample_batch_size=batch_size,
    num_steps=2).prefetch(3)


iterator = iter(dataset)

# (Optional) Optimize by wrapping some of the code in a graph using TF function.
agent.train = common.function(agent.train)

# Reset the train step
agent.train_step_counter.assign(0)

# Evaluate the agent's policy once before training.
avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)

returns = [avg_return]

for _ in range(num_iterations):
    # Collect a few steps using collect_policy and save to the replay buffer.
    for _ in range(collect_steps_per_iteration):
        collect_step(train_env, agent.collect_policy)

    # Sample a batch of data from the buffer and update the agent's network.
    experience, unused_info = next(iterator)
    train_loss = agent.train(experience)
    step = agent.train_step_counter.numpy()

    if step % log_interval == 0:
        print('step = {0}: loss = {1}'.format(step, train_loss.loss))

    if step % eval_interval == 0:
        avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
        print('step = {0}: Average Return = {1:.2f}'.format(step, avg_return))
        returns.append(avg_return)

""" Sauvegarde """
my_policy = agent.policy
print(my_policy)
saver = PolicySaver(my_policy, batch_size=None)
saver.save('frenchstone_agent')


steps = range(0, num_iterations + 1, eval_interval)
plt.plot(steps, returns)
plt.ylabel('Average Return')
plt.xlabel('Step')
plt.ylim(bottom=-1)
plt.ylim(top=1)
plt.show()
