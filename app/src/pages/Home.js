import React from 'react';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Row from 'react-bootstrap/Row';
import Chat from '../components/chat/Chat';


class Home extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            chatOpen: false
        };

        this.showChat = this.showChat.bind(this);
        this.handleClose = this.handleClose.bind(this);
    }

    showChat() {
        this.setState({ chatOpen: true });
    }

    handleClose() {
        this.setState({ chatOpen: false });
    }

    render() {
        if (this.state.chatOpen) {
            var chat = <Chat onClose={this.handleClose} server={this.props.server} />;
        }

        return (
            <div>
                <Jumbotron>
                    <Container>
                        <h1>Welcome to Incorpbot</h1>
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
                        <p><Button onClick={this.showChat} disabled={this.state.chatOpen}>Start Chatting &raquo;</Button></p>
                    </Container>
                </Jumbotron>
                <Container>
                    <Row>
                        <Col>
                            <h2>Heading</h2>
                            <p>Donec id elit non mi porta gravida at eget metus. Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui. </p>
                        </Col>
                        <Col>
                            <h2>Heading</h2>
                            <p>Donec id elit non mi porta gravida at eget metus. Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui. </p>
                        </Col>
                        <Col>
                            <h2>Heading</h2>
                            <p>Donec id elit non mi porta gravida at eget metus. Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus. Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui. </p>
                        </Col>
                    </Row>
                </Container>
                {chat}
            </div>
        );
    }
}

export default Home;
