from message_handlers.onboarding import onboarding_sent


def update_pin(event, client):
    channel_id = event.get("channel_id")
    user_id = event.get("user")
    onboarding_tutorial = onboarding_sent[channel_id][user_id]
    onboarding_tutorial.pin_task_completed = True
    msg = onboarding_tutorial.get_message_payload()
    client.chat_update(**msg)