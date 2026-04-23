import os
import re

def process_html(input_file, output_file, is_dark):
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Inject qwebchannel.js and our custom scripts at the end of body
    custom_script = """
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
        var backend;
        var md2html = function(text) {
            // Very simple markdown to HTML (just handling newlines and basic bold for now)
            return text.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
        };

        window.onload = function() {
            if (typeof QWebChannel !== 'undefined') {
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    backend = channel.objects.backend;
                    
                    // Attach to UI events
                    const promptInput = document.getElementById('promptInput');
                    const sendBtn = document.getElementById('sendBtn');
                    const themeToggleBtn = document.getElementById('themeToggleBtn');
                    const settingsBtn = document.getElementById('settingsBtn');
                    const clearBtn = document.getElementById('clearBtn');
                    
                    if (promptInput && sendBtn) {
                        sendBtn.addEventListener('click', function() {
                            const text = promptInput.value.trim();
                            if (text) {
                                backend.send_message(text);
                                promptInput.value = '';
                                sendBtn.disabled = true;
                                sendBtn.classList.remove('opacity-100');
                                sendBtn.classList.add('opacity-50');
                            }
                        });
                        
                        promptInput.addEventListener('input', function() {
                            if (promptInput.value.trim().length > 0) {
                                sendBtn.disabled = false;
                                sendBtn.classList.remove('opacity-50');
                                sendBtn.classList.add('opacity-100');
                            } else {
                                sendBtn.disabled = true;
                                sendBtn.classList.remove('opacity-100');
                                sendBtn.classList.add('opacity-50');
                            }
                        });

                        promptInput.addEventListener('keydown', function(e) {
                            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                                sendBtn.click();
                            }
                        });
                    }

                    if (themeToggleBtn) {
                        themeToggleBtn.addEventListener('click', function() {
                            backend.toggle_theme();
                        });
                    }

                    if (settingsBtn) {
                        settingsBtn.addEventListener('click', function() {
                            backend.open_settings();
                        });
                    }
                    
                    if (clearBtn) {
                        clearBtn.addEventListener('click', function() {
                            backend.clear_chat();
                        });
                    }

                    // Tell backend we are ready
                    backend.page_loaded();
                });
            } else {
                console.error("QWebChannel is not defined. Ensure qrc:///qtwebchannel/qwebchannel.js is loaded.");
            }
        };

        // Functions called by backend
        let currentAiMessageContent = null;
        
        window.clearHistory = function() {
            const canvas = document.getElementById('chatCanvas');
            if (canvas) {
                canvas.innerHTML = '';
            }
        };

        window.addMessage = function(role, content, avatarUrl) {
            const canvas = document.getElementById('chatCanvas');
            if (!canvas) return;
            
            const div = document.createElement('div');
            
            if (role === 'user') {
                div.className = 'flex gap-4 items-start justify-end pl-4 md:pl-12 my-6';
                div.innerHTML = `
                    <div class="bg-primary-container text-on-primary p-4 md:p-6 rounded-2xl rounded-tr-none shadow-md max-w-[85%] break-words">
                        <p class="leading-relaxed body-lg">${md2html(content)}</p>
                    </div>
                `;
            } else {
                div.className = 'flex gap-4 items-start pr-4 md:pr-12 my-6';
                let iconHtml = `<span class="material-symbols-outlined text-on-surface-variant" style="font-variation-settings: 'FILL' 1;">smart_toy</span>`;
                div.innerHTML = `
                    <div class="w-10 h-10 rounded-xl bg-surface-container flex items-center justify-center shrink-0 border border-outline-variant/10">
                        ${iconHtml}
                    </div>
                    <div class="flex flex-col gap-4 max-w-3xl">
                        <div class="bg-surface-container-lowest p-4 md:p-6 rounded-2xl rounded-tl-none shadow-sm border border-outline-variant/10">
                            <p class="text-on-surface leading-relaxed body-md content-p">${md2html(content)}</p>
                        </div>
                    </div>
                `;
            }
            
            canvas.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth', block: 'end' });
            
            if (role === 'assistant') {
                currentAiMessageContent = div.querySelector('.content-p');
            } else {
                currentAiMessageContent = null;
            }
        };

        window.startAiMessage = function() {
            addMessage('assistant', '');
        };

        window.appendAiToken = function(token) {
            if (currentAiMessageContent) {
                // simple append
                currentAiMessageContent.innerHTML += md2html(token);
                currentAiMessageContent.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
        };

        window.finishAiMessage = function() {
            currentAiMessageContent = null;
            const promptInput = document.getElementById('promptInput');
            if (promptInput) promptInput.focus();
        };
        
        window.setAiState = function(isGenerating) {
            const sendBtn = document.getElementById('sendBtn');
            const promptInput = document.getElementById('promptInput');
            if (sendBtn && promptInput) {
                if (isGenerating) {
                    sendBtn.disabled = true;
                    promptInput.disabled = true;
                    sendBtn.classList.remove('opacity-100');
                    sendBtn.classList.add('opacity-50');
                } else {
                    promptInput.disabled = false;
                    if (promptInput.value.trim().length > 0) {
                        sendBtn.disabled = false;
                        sendBtn.classList.remove('opacity-50');
                        sendBtn.classList.add('opacity-100');
                    }
                }
            }
        };
    </script>
    </body>
    """

    # We need to insert IDs into specific elements to bind them
    
    # 1. Textarea
    html = re.sub(
        r'<textarea([^>]*)placeholder="([^"]*Message[^"]*|[^"]*Describe[^"]*)"([^>]*)>',
        r'<textarea id="promptInput" \1placeholder="\2"\3>',
        html
    )
    
    # 2. Send Button (look for send icon)
    html = re.sub(
        r'<button([^>]*)(>[\s\S]*?>send<[\s\S]*?</button>)',
        r'<button id="sendBtn" class="opacity-50" disabled \1\2',
        html
    )

    # 3. Theme toggle button (light_mode icon)
    html = re.sub(
        r'<button([^>]*)(>[\s\S]*?>light_mode<[\s\S]*?</button>)',
        r'<button id="themeToggleBtn" \1\2',
        html
    )

    # 4. Settings button 
    html = re.sub(
        r'<div([^>]*)(>[\s\S]*?>settings<[\s\S]*?</div>)',
        r'<button id="settingsBtn" \1\2'.replace('div', 'button'),
        html
    )
    # the light theme has it as a button already:
    html = re.sub(
        r'<button([^>]*)(>[\s\S]*?>settings<[\s\S]*?</button>)',
        r'<button id="settingsBtn" \1\2',
        html
    )

    # 5. Clear / New chat
    html = re.sub(
        r'<button([^>]*)(>[\s\S]*?>add<[\s\S]*?</button>)',
        r'<button id="clearBtn" \1\2',
        html
    )

    # 6. Chat Canvas Container
    # Find the big scrollable area.
    # Light theme: <div class="flex-grow overflow-y-auto custom-scrollbar p-8 flex flex-col gap-8 max-w-5xl mx-auto w-full">
    # Dark theme: <div class="max-w-4xl mx-auto space-y-12"> inside <div class="flex-1 overflow-y-auto px-6 py-12 scroll-smooth">
    
    # Just replace the whole contents of the scrollable area with our chat canvas.
    if is_dark:
        pattern = r'(<div class="flex-1 overflow-y-auto px-6 py-12 scroll-smooth">)[\s\S]*?(<div class="p-6 relative bg-gradient-to-t)'
        replacement = r'\1\n<div id="chatCanvas" class="max-w-4xl mx-auto space-y-8 flex flex-col pb-20"></div>\n</div>\n\2'
    else:
        pattern = r'(<div class="flex-grow overflow-y-auto custom-scrollbar p-8 flex flex-col gap-8 max-w-5xl mx-auto w-full">)[\s\S]*?(<div class="p-8 pt-0 bg-gradient-[^>]+>)'
        replacement = r'\1\n<div id="chatCanvas" class="flex flex-col w-full pb-20"></div>\n</div>\n\2'

    html = re.sub(pattern, replacement, html)

    # Replace </body> with custom script
    html = html.replace('</body>', custom_script)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    process_html('ai_chatbot_light_theme.html', 'ui_light.html', is_dark=False)
    process_html('ai_chatbot_dark_theme.html', 'ui_dark.html', is_dark=True)
    print("UI files prepared successfully.")
