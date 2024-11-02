import { React, useEffect, useRef } from 'react';
import { useState } from 'react';
import { ThreeDots } from 'react-loader-spinner';
import Switch from 'react-switch';
import Markdown from 'react-markdown';

import css from './Chat.module.css';

//address of server
const server = 'http://192.168.1.197:8200';
//const server = 'http://localhost:8100';
const sourceViewHeight = '45px';

function Chat() {
    //console.log('rendered')
    const [chatHistory, setChatHistory] = useState([]);
    const [docChunks, setDocChunks] = useState([]);
    const [userQuestion, setUserQuestion] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [useChatHistory, setUseChatHistory] = useState(true);
    const bottomRef = useRef(null);

    //handles question and makes request to llm
    async function handleQuestion() {
        setIsGenerating(true); //avoids repeat question
        
        let newChatHistory = [...chatHistory, [userQuestion, ['', []]]];
        setChatHistory(newChatHistory);

        //prepares request body, keep last 3 messages
        let postHistory = chatHistory;
        if (postHistory.length > 3) {
            postHistory = chatHistory.slice(-3);
        }
        postHistory = postHistory.map((value, index) => {
            return [value[0], value[1][0]];
        })
        postHistory = [['hi', 'hi'], ...postHistory]

        //post request options
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                input: {
                    question: userQuestion,
                    chat_history: postHistory
                }
            })
        };
        setUserQuestion(''); //resets user question

        const address = server + '/model' + (useChatHistory ? '/conversational' : '/simple') + '/stream';
        fetch(address, requestOptions)
            .then(async response => {
                console.log(response);
                if (!response.ok) {
                    return Promise.reject(response.status);
                }

                //streaming the response body and handling data
                let data = '';
                let answer = '';
                let sources = [];
                let chunks = [];
                let addedChunks = false;
                for await (let message of response.body) {
                    message = new TextDecoder().decode(message).split(/\r?\n/);
                    for (let i = 0; i < message.length; i++) {
                        if (message[i].slice(0, 7) == 'event: ') {
                            data = data.substring(data.indexOf('{'), data.lastIndexOf('}') + 1);
                            if (data.length < 2) {
                                data = '';
                                continue;
                            }
                            data = JSON.parse(data);
                                
                            if (data["answer"]) {
                                answer += data["answer"];
                                newChatHistory = [...chatHistory, [userQuestion, [answer, []]]];
                                setChatHistory(newChatHistory);
                            }
                            if (data["sources"]) {
                                sources = [...sources, ...data["sources"]];
                            }
                            if (data["chunks"]) {
                                chunks = [...chunks, ...data["chunks"]];
                            }
                            data = '';
                        } else {
                            data += message[i];
                        }
                    }

                    //updates chunks before end of generation
                    if (!addedChunks && chunks.length > 0 && chunks.length == sources.length) {
                        addedChunks = true;
                        for (let i = 0; i < chunks.length; i++) {
                            chunks[i] = sources[i] + ': ' + chunks[i];
                        }
                        setDocChunks([...chunks, ...docChunks]);
                    }
                }

                //setting the chat history and sources
                newChatHistory = [...chatHistory, [userQuestion, [answer, sources]]];
                setChatHistory(newChatHistory);
                setIsGenerating(false);
            })
            .catch(error => {
                console.log('ERROR!', error);
                newChatHistory = [...chatHistory, [userQuestion, ["Error in generating answer! Please try again.", []]]];
                setChatHistory(newChatHistory);
                setIsGenerating(false);
            })
    }

    //handles flag report and posts to backend
    function handleFlag() {
        let comment = prompt("Describe chat or response issue:");
        if (comment == null) {
            return;
        }
        let postHistory = chatHistory.map((value, index) => {
            return [value[0], value[1][0]];
        })

        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                chat: postHistory,
                comment: comment
            })
        };

        const address = server + '/flags';
        fetch(address, requestOptions)
            .then(async response => {
                console.log(response);
            })
            .catch(error => {
                console.log('ERROR!', error);
            })
    }

    //handles getting flags from backend
    function handleGetFlags() {
        const requestOptions = {
            method: 'GET',
            headers: { 'Content-Type': 'application/json'},
        };

        const address = server + '/flags';
        fetch(address, requestOptions)
            .then(async response => {
                console.log(response);
                const data = await response.json();
                console.log(data);
            })
            .catch(error => {
                console.log('ERROR!', error);
            })
    }
    
    //allows sending question with Enter
    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            handleQuestion();
        }
    }

    //brings scroll to bottom when generating
    useEffect(() => {
        bottomRef.current?.scrollIntoView();
    }, [chatHistory]);

    //renders chat messages and reference links
    const conversation = chatHistory.map((value, index) => {
        //console.log(value, index);
        const references = value[1][1].map((value, index) => {
            let filename = value.substring(value.lastIndexOf('/') + 1);
            return (
                <div key={value + index}>
                    <a onClick={() => {
                        const address = server + '/downloadfile/' + value;
                        window.open(address, '_blank').focus()
                    }}
                    >[{index + 1}] {filename} </a>
                </div>
            );
        });
        return (
            <div key={value + index}>
                <li key={value[0] + index + 'user'} className={css['li']}>
                    <div className={css['user-message']}>
                        {value[0]}
                    </div>
                </li>
                <li key={value[1] + index + 'bot'} className={css['li']}>
                    <div className={css['bot-message']}>
                        {value[1][0].length == 0 && (
                            <ThreeDots height="20" width="40" color="#6C6C6D"/>
                        )}
                        <Markdown>
                            {value[1][0]}
                        </Markdown>
                        {value[1][1].length !== 0 && (
                            <div className={css['reference-line']}>
                                References: {references}
                            </div>
                        )}
                    </div>
                </li>
            </div>
        );
    });

    //renders sources tab with chunks
    const chunksSection = docChunks.map((value, index) => {
        let first = value.slice(0, value.indexOf(':'));
        let second = value.substring(value.indexOf(':'));
        return (
            <div key={value + index}>
                <li key={value + index + 'chunk'} className={css['li']}>
                    <div
                        className={css["chunk-container"]}
                        style={{height: sourceViewHeight}}
                        onClick={e => {
                            e.currentTarget.style.height = e.currentTarget.style.height === 'auto' ? sourceViewHeight : 'auto';
                        }}
                    ><b>{first}</b>{second}</div>
                </li>
            </div>    
        );
    });

    return (
        <>
            <div className={css['main-container']}>
                <header className={css['header']}>
                    <h4>JTLS-GO Chatbot</h4>
                    <div className={css['button-group']}>
                        <div className={css['switch-container']}>
                            <p>Conversation aware: </p>
                            <Switch
                                onChange={() => {setUseChatHistory(useChatHistory == true ? false : true)}}
                                checked={useChatHistory}
                                onColor='#23275D'
                            />
                        </div> 
                        <button 
                            className={css['button']}
                            onClick={() => {
                                setChatHistory([]);
                                setDocChunks([]);
                            }}
                        >Clear conversation</button>
                        <button
                            className={css['button']}
                            onClick={handleFlag}
                        >Flag chat</button>
                        <button
                            style={{display: 'none'}}
                            className={css['button']}
                            onClick={handleGetFlags}
                        >Get Flags</button>
                        <button
                            id="show_source_btn"
                            className={css['button']}
                            onClick={(e) => {
                                const elem = document.getElementById('source_container');
                                elem.style.width = elem.style.width === 'auto' ? '0%' : 'auto';
                                elem.style.display = elem.style.display === 'flex' ? 'none' : 'flex';
                                const btn = document.getElementById('show_source_btn');
                                btn.innerHTML = btn.innerHTML === 'Show sources' ? 'Hide sources' : 'Show sources';
                            }}
                        >Show sources</button>
                    </div>
                </header>
                <div className={css['horizontal-container']}>
                    <div className={css['chat-container']}>
                        <div className={css['scroll-bar']}>
                            <div className={css['chat-welcome']}>
                            Ask your JTLS-GO related questions and view the answer based on the official documentation.
                            Open the documents by clicking the Reference links or view the relevant sections in the Sources tab.
                            Use complete names and terms and report chat issues with the Flag option.
                            When not conversation aware write full standalone questions.
                            Enjoy!
                            </div>
                            <ol className={css['ol']}>{conversation}</ol>
                            <div ref={bottomRef} />
                        </div> 
                        <div className={css['input-section']}>
                            <input
                                className={css['input']}
                                placeholder='Enter a question...'
                                value={userQuestion}
                                onChange={e => setUserQuestion(e.target.value)}
                                onKeyDown={handleKeyDown}
                            />
                            <button
                                className={css['button']}
                                onClick={handleQuestion}
                                disabled={isGenerating}
                            >Send</button>
                        </div>
                    </div>
                    <div id="source_container"
                        className={css['source-container']}
                        style={{width: 'auto', display: 'none'}}
                    >
                        <ol className={css['ol']}>{chunksSection}</ol>
                    </div>
                </div>
            </div>
        </>
    );
}

export default Chat;