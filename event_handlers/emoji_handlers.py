from event_handlers.onboarding_tutorial import onboarding_tutorials_sent


def update_emoji(event, client):
    channel_id = event.get("item", {}).get("channel")
    user_id = event.get("user")

    if channel_id not in onboarding_tutorials_sent:
        return

    onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]
    onboarding_tutorial.reaction_task_completed = True
    msg = onboarding_tutorial.get_message_payload()
    client.chat_update(**msg)