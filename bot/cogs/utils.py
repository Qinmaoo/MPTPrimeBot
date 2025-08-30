def create_message_classic(prime, embed):
	player_pay = prime['player_to_pay_id']
	is_collected = "✅" if prime["collected"] else "❌"
	claim_line = f"📌 **Réclamée :** ❌\n"

	paying_line = f"👤 **Payeur :** <@{player_pay}>\n"
	if prime["is_claimed"]:
		player_claim = prime["player_who_claimed_id"]
		if player_claim:
			claim_line = f"📌 **Réclamée ✅ par :** <@{player_claim}>\n"

	embed.add_field(
		name=f"{prime['player_wanted']} ({prime['characters_played']})",
		value=(
			f"💰 **Récompense :** {prime['reward']}\n"
			f"{paying_line}"
			f"{claim_line}"
			f"**Récupérée :** {is_collected}"
		),
		inline=False
	)