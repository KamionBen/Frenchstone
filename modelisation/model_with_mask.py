import keras.optimizers.schedules.learning_rate_schedule
import matplotlib.pyplot as plt
from tf_agents.agents.dqn import dqn_agent
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.networks import sequential
from tf_agents.policies import q_policy, PolicySaver
from tf_agents.trajectories import trajectory
from tf_agents.specs import tensor_spec
from tf_agents.utils import common
from engine import *


def generate_legal_vector(state):
    """ Gestion des actions légales """
    legal_actions = [True]
    gamestate = state.get_gamestate()
    for i in range(90):
        legal_actions.append(False)

    """ Quelles cartes peut-on jouer ? """
    for i in range(int(gamestate["nbre_cartes_j"])):
        if gamestate["mana_dispo_j"] >= gamestate[f"carte_en_main{i + 1}_cost"] > -99 and gamestate[f"pv_serv7_j"] == -99:
            legal_actions[i+1] = True

    """ Quelles cibles peut-on attaquer et avec quels attaquants"""
    """ Notre héros peut attaquer """
    if gamestate["remaining_atk_j"] > 0 and gamestate["attaque_j"] > 0:
        legal_actions[11] = True
        for j in range(1, 8):
            if gamestate[f"atq_serv{j}_adv"] != -99:
                legal_actions[11 + j] = True

    """ Nos serviteurs peuvent attaquer """
    for i in range(1, 8):
        if gamestate[f"atq_remain_serv{i}_j"] > 0:
            legal_actions[11 + 8 * i] = True
            for j in range(1, 8):
                if gamestate[f"atq_serv{j}_adv"] != -99:
                    legal_actions[11 + 8 * i + j] = True

    if gamestate["dispo_ph_j"] and gamestate["cout_ph_j"] <= gamestate["mana_dispo_j"]:
        targets = state.targets_hp()
        if state.players[0].hero in targets:
            legal_actions[75] = True
        if state.players[1].hero in targets:
            legal_actions[83] = True
        for i in range(1, 8):
            if gamestate[f"atq_serv{i}_j"] != -99:
                if gamestate[f"serv{i}_j"] in targets:
                    legal_actions[75 + i] = True
            if gamestate[f"atq_serv{i}_adv"] != -99:
                if gamestate[f"serv{i}_adv"] in targets:
                    legal_actions[83 + i] = True

    return legal_actions


def estimated_advantage(action, state):
    """ Simule le plateau qu'aurait donné une certaine action pour en tirer une notion d'avantage gagné ou perdu """
    actual_state = deepcopy(state)
    next_state = deepcopy(state)
    action = int(action)

    if action == 0:
        TourEnCours(next_state).fin_du_tour()
        while next_state.get_gamestate()['pseudo_j'] == 'OldIA':
            next_state = Orchestrator().tour_oldia_training(next_state, old_policy, oldpolicy_state)
            if not next_state.game_on:
                if next_state.winner.name == "NewIA":
                    return 500
                else:
                    return -500
    elif action < 11:
        TourEnCours(next_state).jouer_carte(next_state.players[0].hand[action - 1])
    elif 11 <= action < 75:
        if (action - 11) // 8 == 0:
            attacker = next_state.players[0].hero
        else:
            attacker = next_state.players[0].servants[int((action - 11) // 8 - 1)]
        if (action - 11) % 8 == 0:
            target = next_state.players[1].hero
        else:
            target = next_state.players[1].servants[int((action - 11) % 8 - 1)]
        TourEnCours(next_state).attaquer(attacker, target)
    elif action >= 75:
        if action == 75:
            target = next_state.players[0].hero
        elif action == 83:
            target = next_state.players[1].hero
        elif action < 83:
            target = next_state.players[0].servants[action - 76]
        else:
            target = next_state.players[1].servants[action - 84]
        TourEnCours(next_state).pouvoir_heroique(next_state.players[0].classe, target)

    next_state.update()

    if not next_state.game_on:
        if next_state.winner.name == "NewIA":
            return 500
        else:
            return -500

    def calc_advantage(state):
        advantage = (state["nbre_cartes_j"] - state["nbre_cartes_adv"]) + 0.8 * (state["nbre_cartes_j"] / max(1, state["nbre_cartes_adv"]))
        for i in range(1, 8):
            if state[f"serv{i}_j"] != -99:
                advantage += 1.5 * state[f"atq_serv{i}_j"] + 1.5 * state[f"pv_serv{i}_j"]
            if state[f"serv{i}_adv"] != -99:
                advantage -= 1.5 * state[f"atq_serv{i}_adv"] + 1.5 * state[f"pv_serv{i}_adv"]
        advantage += 0.25 * (pow(30 - state["pv_adv"], 1.3) - pow(30 - state["pv_j"], 1.3))
        advantage += state["attaque_j"]
        return advantage

    actual_advantage = calc_advantage(actual_state.get_gamestate())
    predicted_advantage = calc_advantage(next_state.get_gamestate())


    # print(actual_state.get_gamestate())
    # print(f"Avantage en cours : {actual_advantage}")
    # print(action)
    # print(next_state.get_gamestate())
    # print(f"Avantage prévu : {predicted_advantage}")
    # print('-------------------------------------------')

    return round(predicted_advantage - actual_advantage, 2)


players = [Player("NewIA", "Mage"), Player("OldIA", "Chasseur")]
plateau_depart = Plateau(players)
classes_heros = ["Mage", "Chasseur", "Paladin", "Chasseur de démons", "Druide", "Voleur", "Démoniste", "Guerrier",
                 "Chevalier de la mort"]

columns_actual_state = ["mana_dispo_j", "mana_max_j", "mana_max_adv", "pv_j", "pv_adv", "nbre_cartes_j",
                        "nbre_cartes_adv", "armor_j", "armor_adv", "attaque_j", "remaining_atk_j"]

""" HERO """
for classe_heros in classes_heros:
    columns_actual_state.append(f"is_{classe_heros}")

""" HAND """
for i in range(10):
    columns_actual_state.append(f"carte_en_main{i + 1}_cost")
    columns_actual_state.append(f"carte_en_main{i + 1}_atk")
    columns_actual_state.append(f"carte_en_main{i + 1}_pv")

""" SERVANTS """
for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_j")
    columns_actual_state.append(f"pv_serv{i + 1}_j")
    columns_actual_state.append(f"atq_remain_serv{i + 1}_j")

for i in range(7):
    columns_actual_state.append(f"atq_serv{i + 1}_adv")
    columns_actual_state.append(f"pv_serv{i + 1}_adv")


class Frenchstone(py_environment.PyEnvironment):
    def __init__(self):
        self._action_spec = array_spec.BoundedArraySpec(shape=(), dtype=np.int32, minimum=0, maximum=90, name='action')
        self._state = plateau_depart
        self._observation_spec = {
            'observation': array_spec.BoundedArraySpec(shape=(len(itemgetter(*columns_actual_state)(self._state.get_gamestate())),), dtype=np.int32, minimum=-100, maximum=100, name='observation'),
            'valid_actions': array_spec.ArraySpec(name="valid_actions", shape=(91,), dtype=np.bool_)
        }
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        if bool(random.getrandbits(1)):
            self._state = Plateau([Player("NewIA", random.choice(classes_heros)),
                                   Player("OldIA", random.choice(classes_heros))])
        else:
            self._state = Plateau([Player("OldIA", random.choice(classes_heros)),
                                   Player("NewIA", random.choice(classes_heros))])
            while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
                self._state = Orchestrator().tour_oldia_training(self._state, old_policy, oldpolicy_state)
        self._episode_ended = False
        obs = self.observation_spec()

        """ Gestion des actions légales """
        legal_actions = generate_legal_vector(self._state)

        obs['observation'] = np.array(itemgetter(*columns_actual_state)(self._state.get_gamestate()))
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        return ts.restart(obs)

    def _step(self, action):

        if self._episode_ended:
            return self.reset()

        """ Estimation de la récompense """
        reward = estimated_advantage(action, self._state)
        # reward = 0

        """ Gestion des actions légales """
        self._state = Orchestrator().tour_ia_training(self._state, action)

        while self._state.get_gamestate()['pseudo_j'] == 'OldIA':
            self._state = Orchestrator().tour_oldia_training(self._state, old_policy, oldpolicy_state)

        legal_actions = generate_legal_vector(self._state)
        obs = self.observation_spec()
        obs['observation'] = np.array(itemgetter(*columns_actual_state)(self._state.get_gamestate()), dtype=np.int32)
        obs['valid_actions'] = np.array(legal_actions, dtype=np.bool_)
        if reward in [-500, 500]:
            self._episode_ended = True
            return ts.termination(obs, reward)
        return ts.transition(obs, reward)


train_env = Frenchstone()
eval_env = Frenchstone()
train_env = tf_py_environment.TFPyEnvironment(train_env, check_dims=True)
eval_env = tf_py_environment.TFPyEnvironment(eval_env, check_dims=True)
time_step = train_env.reset()

num_iterations = 100000  # @param {type:"integer"}
initial_collect_steps = 10  # @param {type:"integer"}
collect_steps_per_iteration = 50  # @param {type:"integer"}
replay_buffer_capacity = 60000  # @param {type:"integer"}

batch_size = 512  # @param {type:"integer"}
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=1e-6,
    decay_steps=10000,
    decay_rate=0.9)

log_interval = 200  # @param {type:"integer"}

num_eval_episodes = 100  # @param {type:"integer"}
eval_interval = 1000  # @param {type:"integer"}

fc_layer_params = (300, 250, 200, 100, 50, 30)
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
q_net = sequential.Sequential([mask_layer] + dense_layers + [q_values_layer] + [flatten_layer])

optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)

train_step_counter = tf.Variable(0)
# Epsilon decay
epsilon = keras.optimizers.schedules.learning_rate_schedule.PolynomialDecay(
    1.0,
    80000,
    0.05,
    power=0.8
)


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
    epsilon_greedy=epsilon(train_step_counter))


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
        # print(timestep)
        # print(episode_return)
        # print('----------------------------------------------------------')
        total_return += episode_return

    average_return = total_return / num_episodes
    return average_return.numpy()[0]


# random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(),
#                                                 train_env.action_spec())


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
    # print(timestep)
    # print('-------------------------------------------------')
    action_step = policy.action(timestep)
    # print(policy._action_spec)
    # print(policy.policy_state_spec)
    # print(policy.policy_step_spec)
    # print(action_step)
    # print('-------------------------------------------------')
    next_time_step = environment.step(action_step.action)
    # print(next_time_step)
    # print('-------------------------------------------------')
    traj = trajectory.from_transition(timestep, action_step, next_time_step)
    # Add trajectory to the replay buffer
    replay_buffer.add_batch(traj)
    # print('-------------------------------------------------')
    # print('-------------------------------------------------')
    # print('-------------------------------------------------')


for _ in range(initial_collect_steps):
    collect_step(train_env, q_policy)

# This loop is so common in RL, that we provide standard implementations of
# these. For more details see the drivers module.

# Dataset generates trajectories with shape [BxTx...] where
# T = n_step_update + 1.
dataset = replay_buffer.as_dataset(
    num_parallel_calls=10, sample_batch_size=batch_size,
    num_steps=2).prefetch(10)


iterator = iter(dataset)

# (Optional) Optimize by wrapping some of the code in a graph using TF function.
agent.train = common.function(agent.train)

# Reset the train step
agent.train_step_counter.assign(0)

# Evaluate the agent's policy once before training.
avg_return = compute_avg_return(eval_env, agent.policy, 10)

returns = []
returns2 = []

for _ in range(num_iterations):
    # Collect a few steps using collect_policy and save to the replay buffer.
    for _ in range(collect_steps_per_iteration):
        collect_step(train_env, agent.collect_policy)

    # Sample a batch of data from the buffer and update the agent's network.
    experience, unused_info = next(iterator)
    train_loss = agent.train(experience)
    step = agent.train_step_counter.numpy()
    if step % 1000 < 750:
        agent._epsilon_greedy = epsilon(train_step_counter)
        agent.collect_policy._epsilon = epsilon(train_step_counter)
    else:
        agent._epsilon_greedy = 0.0
        agent.collect_policy._epsilon = 0.0

    if step % log_interval == 0:
        print('step = {0}: loss = {1}'.format(step, train_loss.loss))

    if step % eval_interval == 0:
        my_policy = agent.policy
        my_policy2 = agent.collect_policy
        saver = PolicySaver(my_policy, batch_size=None)
        saver2 = PolicySaver(my_policy2, batch_size=None)
        saver.save(f"frenchstone_agent_v0.02-a-{step}")
        saver2.save(f"frenchstone_agent_v0.02-b-{step}")
        avg_return = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
        avg_return2 = compute_avg_return(eval_env, agent.collect_policy, num_eval_episodes)
        print('step = {0}: Average Return = {1:.2f}'.format(step, avg_return))
        print('step = {0}: Average Return Collect = {1:.2f}'.format(step, avg_return2))
        returns.append(avg_return)
        returns2.append(avg_return2)

""" Sauvegarde """
my_policy = agent.policy
saver = PolicySaver(my_policy, batch_size=None)
saver.save('frenchstone_agent_v0.02-a')

my_policy2 = agent.collect_policy
saver = PolicySaver(my_policy2, batch_size=None)
saver.save('frenchstone_agent_v0.02-b')


steps = range(0, num_iterations, eval_interval)
plt.plot(steps, returns)
plt.plot(steps, returns2)
plt.ylabel('Average Return')
plt.xlabel('Step')
plt.ylim(bottom=-600)
plt.ylim(top=600)
plt.show()