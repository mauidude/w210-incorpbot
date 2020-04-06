import moment from 'moment';
import React from 'react';
import Button from 'react-bootstrap/Button';
import Nav from 'react-bootstrap/Nav';
import ReactGA from 'react-ga';
import socketIOClient from "socket.io-client";
import './Chat.css';
import History from './History';
import Input from './Input';

class Chat extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            history: [],
            pending: false,
        };

        this.sendMessage = this.sendMessage.bind(this);
        this.receiveWelcome = this.receiveWelcome.bind(this);
        this.receiveMessage = this.receiveMessage.bind(this);
        this.receiveEndResponse = this.receiveEndResponse.bind(this);
        this.handleClose = this.handleClose.bind(this);
    }

    componentDidMount() {
        this.websocket = socketIOClient(`http://${this.props.server}`);
        this.websocket.on('conversation:response:end', this.receiveEndResponse);
        this.websocket.on('conversation:welcome', this.receiveWelcome);
        this.websocket.on('conversation:response', this.receiveMessage);

        this.setState({
            pending: true
        });

        // start a new conversation
        setTimeout(() => {
            this.websocket.emit('conversation:new');
        }, 250);
    }

    sendMessage(msg) {
        this.setState({ history: [...this.state.history, { message: msg, sender: "me" }] });
        this.setState({ pending: true });

        this.websocket.emit('conversation:message', { message: msg, conversation_id: this.state.conversation_id });
    }

    receiveMessage(data) {
        this.setState({
            history: [...this.state.history, { message: data.message, sender: "you", html: data.html }],
        });
    }

    receiveEndResponse() {
        this.setState({
            pending: false
        });
    }

    receiveWelcome(data) {
        this.receiveMessage(data);
        this.setState({ conversation_id: data.conversation_id, start: moment() });

        ReactGA.set({
            conversation_id: this.state.conversation_id
        });


        ReactGA.event({
            category: 'User',
            action: 'Started chat'
        });

        console.log({ conversation_id: this.state.conversation_id });
    }

    handleClose(e) {
        e.preventDefault();
        this.props.onClose();

        ReactGA.event({
            category: 'User',
            action: 'Ended chat'
        });

        var duration = moment.duration(moment().diff(this.state.start));
        ReactGA.timing({
            category: 'Chat',
            variable: 'duration',
            value: duration.as('seconds')
        });
    }

    render() {
        return (
            <div className="Chat">
                <Nav className="justify-content-end">
                    <Nav.Link>
                        <Button variant="link" onClick={this.handleClose}>&times;</Button>
                    </Nav.Link>
                </Nav>
                <History dialog={this.state.history} pending={this.state.pending} />
                <Input onMessage={this.sendMessage} />
            </div>
        )
    }
}

export default Chat;
