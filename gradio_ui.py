import json
import time
import model
import gradio as gr

with open("prompts.json", "r") as f:
    pre_defined_prompts = json.load(f)


def gpt35_layout():
    with gr.Blocks() as b:
        with gr.Row():
            with gr.Column(scale=4):
                # Prompt Block
                gr.Markdown("<h4>Prompt调试</h4>")
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            roles_drop = gr.Dropdown(choices=pre_defined_prompts.keys(),
                                                     value="default",
                                                     label="预定义系统角色",
                                                     interactive=True)

                        with gr.Row():
                            prompt_box = gr.Textbox(label="系统Prompt",
                                                    value=pre_defined_prompts[roles_drop.value],
                                                    lines=8,
                                                    max_lines=8,
                                                    interactive=True)

                        with gr.Row():
                            custom_btn = gr.Button('自定义设定')
                            submit_prompt_btn = gr.Button("发布设定")

                # model param
                gr.Markdown("<h4>参数</h4>")
                with gr.Row():
                    with gr.Column(variant="panel"):
                        with gr.Row():
                            temperature = gr.Slider(minimum=0.0,
                                                    maximum=1.0,
                                                    step=0.1,
                                                    label='Temperature',
                                                    # info="该值越大使得输出更具创造性",
                                                    interactive=True,
                                                    value=0.1)
                            top_p = gr.Slider(minimum=0.0,
                                              maximum=1.0,
                                              step=0.1,
                                              label='Top P',
                                              # info="该值越小使得输出更具创造性",
                                              interactive=True,
                                              value=1.0)
                        with gr.Row():
                            freq_penalty = gr.Slider(minimum=-2.0,
                                                     maximum=2.0,
                                                     step=0.1,
                                                     label='Frequency Penalty',
                                                     # info="该值越大使得输出越不可能出现重复词",
                                                     interactive=True,
                                                     value=0.0)
                            presence_penalty = gr.Slider(minimum=-2.0,
                                                         maximum=2.0,
                                                         step=0.1,
                                                         label='Presence Penalty',
                                                         # info="该值越小使得输出越有可能出现新词",
                                                         interactive=True,
                                                         value=0.0)
                        with gr.Row():
                            max_token = gr.Slider(minimum=20,
                                                  maximum=4096,
                                                  step=1,
                                                  # info="gpt35的最大token限制为4096",
                                                  label='Max Token',
                                                  interactive=True,
                                                  value=800)

            with gr.Column(scale=6):
                gr.Markdown("<h4>聊天</h4>")

                chat_box = gr.Chatbot(elem_id="chat-box", show_label=False).style(height=600)

                with gr.Row():
                    input_message = gr.Textbox(placeholder="输入你的内容,按shift+Enter发送",
                                               show_label=False,
                                               lines=3,
                                               max_lines=3,
                                               elem_id="chat-input").style(container=False)
                    chat_revoke_btn = gr.Button("清空", elem_id="chat_revoke").style(full_width=False)

        # callback function
        def forbid_prompt_submit():
            return {
                roles_drop: gr.update(interactive=False),
                prompt_box: gr.update(interactive=False),
                submit_prompt_btn: gr.update(interactive=False),
                custom_btn: gr.update(interactive=False),
            }

        def custom_setting():
            return {
                prompt_box: gr.update(placeholder="请输入prompt...", value=None),
                roles_drop: gr.update(value="custom"),
            }

        def pre_defined(a):
            return {prompt_box: gr.update(value=pre_defined_prompts[a])}

        def respond(query, chat_history, prompt, temperature, top_p, freq_penalty, presence_penalty,
                    max_tokens):
            history = []
            for user_msg, ai_msg in chat_history:
                history.append({"role": "user", "content": user_msg})
                history.append({"role": "assistant", "content": ai_msg})

            res = ""
            chat_history.append((query, res))
            for r in model.ChatGPT(prompt).stream_with_history(query, history,
                                                               temperature=temperature,
                                                               top_p=top_p,
                                                               presence_penalty=presence_penalty,
                                                               frequency_penalty=freq_penalty,
                                                               max_tokens=max_tokens):
                res += r
                chat_history[-1] = (query, res)
                time.sleep(0.01)
                yield {input_message: "", chat_box: chat_history}
            yield {input_message: "", chat_box: chat_history}

        # bind component
        roles_drop.input(pre_defined, inputs=[roles_drop], outputs=[prompt_box])
        custom_btn.click(custom_setting, inputs=[], outputs=[prompt_box, roles_drop])
        submit_prompt_btn.click(forbid_prompt_submit,
                                inputs=[],
                                outputs=[roles_drop, prompt_box, custom_btn, submit_prompt_btn])

        input_message.submit(forbid_prompt_submit, inputs=[],
                             outputs=[roles_drop, prompt_box, custom_btn, submit_prompt_btn])

        input_message.submit(respond,
                             inputs=[input_message, chat_box, prompt_box, temperature, top_p,
                                     freq_penalty, presence_penalty, max_token],
                             outputs=[input_message, chat_box])

        chat_revoke_btn.click(lambda p: "", inputs=[chat_box], outputs=[chat_box])

    return {"block": b, "label": "gpt35"}


def create_ui():
    tabs = [gpt35_layout()]
    with gr.Blocks(title="prompt") as ui:
        with gr.Tabs(elem_id="tabs"):
            for t in tabs:
                with gr.TabItem(label=t["label"], id=t["label"], elem_id="tab_" + t["label"]):
                    t["block"].render()
    return ui
