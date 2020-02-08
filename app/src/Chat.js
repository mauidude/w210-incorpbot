import React from 'react';
import Button from 'react-bootstrap/Button';
import Nav from 'react-bootstrap/Nav';
import socketIOClient from "socket.io-client";
import './Chat.css';
import History from './History';
import Input from './Input';

class Chat extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            history: [],
            pending: false
        };

        this.sendMessage = this.sendMessage.bind(this);
        this.receiveMessage = this.receiveMessage.bind(this);
        this.handleClose = this.handleClose.bind(this);
    }

    componentDidMount() {
        this.websocket = socketIOClient('http://localhost:5000');
        this.websocket.on('conversation:response', this.receiveMessage);

        this.setState({
            pending: true
        });

        setTimeout(() => {
            this.websocket.emit('conversation:new');
        }, 1000);
    }

    sendMessage(msg) {
        this.setState({ history: [...this.state.history, { message: msg, sender: "me" }] });
        this.setState({ pending: true });

        this.websocket.emit('conversation:message', { message: msg });
    }

    receiveMessage(data) {
        this.setState({ history: [...this.state.history, { message: data.message, sender: "you" }], pending: false });
    }

    handleClose(e) {
        e.preventDefault();
        this.props.onClose();
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
