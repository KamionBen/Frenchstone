import matplotlib.pyplot as plt
from tf_agents.agents.dqn import dqn_agent
from tf_agents.agents.categorical_dqn import categorical_dqn_agent
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.networks import sequential
from tf_agents.policies import random_tf_policy, q_policy, PolicySaver
from tf_agents.trajectories import trajectory
from tf_agents.specs import tensor_spec
from tf_agents.utils import common
from modelisation.engine import *


def generate_legal_vector(state):
    """ Gestion des actions légales """
    legal_actions = [True]
    for i in range(74):
        legal_actions.append(False)

    """ Quelles cartes peut-on jouer ? """
    for i in range(int(state["nbre_cartes_j"])):
        if state[f"carte_en_main{i + 1}_cost"] <= state["mana_dispo_j"] and state[f"carte_en_main{i + 1}_cost"] != -99\
                and state[f"pv_serv7_j"] == -99:
            legal_actions[i+1] = True
            break

    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    for i in range(1, 8):
        if state[f"atq_remain_serv{i}_j"] > 0:
            legal_actions[11 + 8 * i] = True
            for j in range(1, 8):
                if state[f"atq_serv{j}_adv"] != -99:
                    legal_actions[11 + 8 * i + j] = True
    return legal_actions


def estimated_advantage(action, state):
    """ Simule le plateau qu'aurait donné une certaine action pour en tirer une notion d'avantage gagné ou perdu """
    card_advantage = 0
    board_advantage = 0
    health_advantage = 0

    if action == 0:
        card_advantage -= 1
    elif action <= 10:
        card_advantage -= 1
        board_advantage += 0.3 * state[f"carte_en_main{action}_atk"]
        board_advantage += 0.3 * state[f"carte_en_main{action}_pv"]
    else:
        attacker = state[f"atq_serv{(action - 11) // 8}_j"], state[f"pv_serv{(action - 11) // 8}_j"]
        if (action - 11) % 8 == 0:
            if state["pv_adv"] - attacker[0] <= 0:
                return 100
            else:
                health_advantage += attacker[0]
        else:
            defender = state[f"atq_serv{(action - 11) % 8}_adv"], state[f"pv_serv{(action - 11) % 8}_adv"]
            if attacker[0] >= defender[1]:
                if defender[0] >= attacker[1]:
                    board_advantage += defender[0] + defender[1] - attacker[0] - attacker[1]
                else:
                    board_advantage += defender[1]
            else:
                if defender[0] >= attacker[1]:
                    board_advantage += attacker[0] - attacker[1]
                else:
                    board_advantage += attacker[0] - defender[0]
    coef_cards, coef_board, coef_health = 0.5, 2.5, 1
    return round(coef_cards * card_advantage + coef_board * board_advantage + coef_health * health_advantage, 2)


players = [Player("NewIA", "Mage"), Player("OldIA", "Chasseur")]
plateau_depart = Plateau(players)

columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j", "nbre_cartes_adv"]

for i in range(10):
    columns_actual_state.append(f"carte_en_main{i + 1}_cost")
    columns_actual_state.append(f"carte_en_main{i + 1}_atk")
    columns_actual_state.append(f"carte_en_main{i + 1}_pv")

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_j")
    columns_actual_state.append(f"pv_serv{i + 1}_j")
    columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_adv")
    columns_actual_state.append(f"pv_serv{i + 1}_adv")


class Frenchstone(py_environment.PyEnvironment):
    def __init__(self):
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=74, name='action')
        self._state = plateau_depart
        self._observation_spec = {
            'observation': array_spec.BoundedArraySpec(shape=(len(itemgetter(*columns_actual_state)(self._state.get_gamestate())),), dtype=np.int32, minimum=-100, maximum=100, name='observation'),
            'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(75,), dtype=np.bool_)
        }
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        if bool(random.getrandbits(1)):
            self._state = Plateau([Player("NewIA", "Mage"), Player("OldIA", "Chasseur")])
        else:
            self._state = Plateau([Player("OldIA", "Chasseur"), Player("NewIA", "Mage")])
            while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
                self._state = Orchestrator().tour_oldia_training(self._state, old_policy, oldpolicy_state)
        self._episode_ended = False
        obs = self.observation_spec()

        """ Gestion des actions légales """
        legal_actions = generate_legal_vector(self._state.get_gamestate())

        obs['observation'] = np.array(itemgetter(*columns_actual_state)(self._state.get_gamestate()))
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        return ts.restart(obs)

    def _step(self, action):

        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        """ Estimation de la récompense """
        reward = estimated_advantage(action, self._state.get_gamestate())

        """ Gestion des actions légales """
        self._state = Orchestrator().tour_ia_training(self._state, action)

        legal_actions = generate_legal_vector(self._state.get_gamestate())
        obs = self.observation_spec()
        obs['observation'] = np.array(itemgetter(*columns_actual_state)(self._state.get_gamestate()), dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)

        if not self._state.game_on:
            self._episode_ended = True
            return ts.termination(obs, reward)

        while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
            self._state = Orchestrator().tour_oldia_training(self._state, old_policy, oldpolicy_state)
            if not self._state.game_on:
                reward = -100
                self._episode_ended = True
                return ts.termination(obs, reward)

        legal_actions = generate_legal_vector(self._state.get_gamestate())
        obs = self.observation_spec()
        obs['observation'] = np.array(itemgetter(*columns_actual_state)(self._state.get_gamestate()), dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        return ts.transition(obs, reward)



train_env = Frenchstone()
eval_env = Frenchstone()
train_env = tf_py_environment.TFPyEnvironment(train_env, check_dims=True)
eval_env = tf_py_environment.TFPyEnvironment(eval_env, check_dims=True)
time_step = train_env.reset()

num_iterations = 70000  # @param {type:"integer"}
initial_collect_steps = 1  # @param {type:"integer"}
collect_steps_per_iteration = 30  # @param {type:"integer"}
replay_buffer_capacity = 100000  # @param {type:"integer"}

batch_size = 1024  # @param {type:"integer"}
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=1e-5,
    decay_steps=5000,
    decay_rate=0.9)
log_interval = 100  # @param {type:"integer"}

num_eval_episodes = 100  # @param {type:"integer"}
eval_interval = 1000  # @param {type:"integer"}

fc_layer_params = (250, 128, 100, 50, 25)
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
# with num_actions units to generate one q_value per available action as
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


def observation_action_splitter(obs):
    return obs['observation'], obs['valid_actions']


agent = dqn_agent.DdqnAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=common.element_wise_squared_loss,
    train_step_counter=train_step_counter,
    observation_and_action_constraint_splitter=observation_action_splitter,
    boltzmann_temperature=None,
    epsilon_greedy=0.1)

agent.initialize()


def compute_avg_return(environment, policy, num_episodes=10):
    total_return = 0.0
    for _ in range(num_episodes):
        timestep = environment.reset()
        episode_return = 0.0

        while not timestep.is_last():
            # print('-----------------------------------------')
            # print('-----------------------------------------')
            # print('-----------------------------------------')
            # print('-----------------------------------------')
            # print(timestep)
            action_step = policy.action(timestep)
            # print(action_step)
            timestep = environment.step(action_step.action)
            # print('-----------------------------------------')
            # print(timestep)
            episode_return += timestep.reward
        total_return += episode_return

    avg_return = total_return / num_episodes
    return avg_return.numpy()[0]


random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(),
                                                train_env.action_spec())


""" Relance du dernier modèle """
# q_policy = tf.compat.v2.saved_model.load('frenchstone_agent_v0.02a')
# policy_state = q_policy.get_initial_state(batch_size=512)
"""-------------------------------------------------"""

""" Entraînement d'un nouveau modèle """
q_policy = q_policy.QPolicy(train_env.time_step_spec(),
                            train_env.action_spec(),
                            q_net,
                            observation_and_action_constraint_splitter=observation_action_splitter)
"""-------------------------------------------------"""


compute_avg_return(eval_env, q_policy, 10)

# @test {"skip": true}
replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=train_env.batch_size,
    max_length=replay_buffer_capacity)


def collect_step(environment, policy):
    timestep = environment.current_time_step()
    action_step = policy.action(timestep)
    next_time_step = environment.step(action_step.action)
    # print(timestep)
    # print('-------------------------------------------------')
    # print(action_step)
    # print('-------------------------------------------------')
    # print(next_time_step)
    # print('-------------------------------------------------')
    # print('-------------------------------------------------')
    # print('-------------------------------------------------')
    traj = trajectory.from_transition(timestep, action_step, next_time_step)

    # Add trajectory to the replay buffer
    replay_buffer.add_batch(traj)


for _ in range(initial_collect_steps):
    collect_step(train_env, q_policy)

# This loop is so common in RL, that we provide standard implementations of
# these. For more details see the drivers module.

# Dataset generates trajectories with shape [BxTx...] where
# T = n_step_update + 1.
dataset = replay_buffer.as_dataset(
    num_parallel_calls=5, sample_batch_size=batch_size,
    num_steps=2).prefetch(3)


iterator = iter(dataset)

# (Optional) Optimize by wrapping some of the code in a graph using TF function.
agent.train = common.function(agent.train)

# Reset the train step
agent.train_step_counter.assign(0)

# Evaluate the agent's policy once before training.
avg_return = compute_avg_return(eval_env, agent.policy, 10)

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
saver = PolicySaver(my_policy, batch_size=None)
saver.save('frenchstone_agent_v0.02-a')

my_policy2 = agent.collect_policy
saver = PolicySaver(my_policy2, batch_size=None)
saver.save('frenchstone_agent_v0.02-b')


steps = range(0, num_iterations + 1, eval_interval)
plt.plot(steps, returns)
plt.ylabel('Average Return')
plt.xlabel('Step')
plt.ylim(bottom=-100)
plt.ylim(top=200)
plt.show()