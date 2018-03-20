def CFR(action_history, reach_probs, player_cards):

    if isTerminal(action_history):  # 是不是到了叶子节点
        current_player = len(action_history) % 2
        return getUtility(action_history, player_cards, current_player)

    counterfactual_value_h = 0.0
    counterfactual_value_h_a = [0.0, 0.0]
    current_player = len(action_history) % 2  # 根据当前action history 计算infomation set
    info_set = str(player_cards[current_player])
    for i in range(len(action_history)):
        info_set += str(action_history[i])

    for i in range(2):  # 两种可能的行动 pass 0; bet 1;
        new_action_history = action_history
        new_action_history.append(i)
        new_reach_probs = reach_probs
        new_reach_probs[current_player] = new_reach_probs[current_player] * cur_strategy[info_set + str(i)]
        counterfactual_value_h_a[i] = CFR(new_action_history, new_reach_probs, player_cards)
        counterfactual_value_h += cur_strategy[info_set + str(i)] * counterfactual_value_h_a[i]

    regretSum = 0.0
    for i in range(2):
        regret[info_set + str(i)] += reach_probs[1 - current_player] * (
                counterfactual_value_h_a[i] - counterfactual_value_h)
        AccStrategy[info_set + str(i)] += reach_probs[current_player] * cur_strategy[info_set + str(i)]
        if regret[info_set + str(i)] > 0:
            regretSum += regret[info_set + str(i)]
    for i in range(2):
        if regretSum > 0:
            cur_strategy[info_set + str(i)] = max(0, regret[info_set + str(i)]) / regretSum
        else:
            cur_strategy[info_set + str(i)] = 0.5
        strategySum[info_set + str(i)] += cur_strategy[info_set + str(i)]

    return counterfactual_value_h
