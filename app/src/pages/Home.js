import React from 'react';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Image from 'react-bootstrap/Image';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Row from 'react-bootstrap/Row';
import Chat from '../components/chat/Chat';
import './Home.css';


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
                        <p>Tired of long waits, hefty fees, unhelpful answers to your incorporation questions? Incorpbot is a free tool where you can chat 24/7 with an intelligent resource and ask the questions you have on incorporation, compliance, and other legal matters blocking you from launching your business. Stay informed on state-specific rules and regulations related to corporate structuring in the United States and on top of deadlines and filing requirements.</p>
                        <p><Button onClick={this.showChat} disabled={this.state.chatOpen}>Start Chatting &raquo;</Button></p>
                    </Container>
                </Jumbotron>
                <Container>
                    <Row>
                        <Col>
                            <h2>Services</h2>
                            <p>Incorpbot covers incorporation and patents for multiple US states. See below for the full list. Begin chatting now to discover what else it can do!</p>
                        </Col>
                        <Col>
                            <h2>Why Us</h2>
                            <p>Save time and money by asking your preliminary legal questions here before visiting a lawyer. Reduce your billable hours and become your own legal expert with Incorpbot!</p>
                        </Col>
                        <Col>
                            <h2>Our Data</h2>
                            <p>We pull data from many official sources, compile them, and feed them to our machine learning algorithm to give you the answers you need. Check back often to see if your state is supported!</p>
                        </Col>
                    </Row>
                </Container>
                <Container>
                    <h3>Supported States</h3>

                    <Row>
                        <Col>
                            <Image className="flag california" alt="California" src="/images/flags/california_flag.png" fluid />
                            <span className="label">California</span>
                        </Col>
                        <Col>
                            <Image className="flag delaware" alt="Delaware" src="/images/flags/delaware_flag.png" fluid />
                            <span className="label">Delaware</span>
                        </Col>
                        <Col>
                            <Image className="flag nevada" alt="Nevada" src="/images/flags/nevada_flag.png" fluid />
                            <span className="label">Nevada</span>
                        </Col>
                        <Col>
                            <Image className="flag new-york" alt="New York" src="/images/flags/new_york_flag.png" fluid />
                            <span className="label">New York</span>
                        </Col>
                        <Col>
                            <Image className="flag texas" alt="Texas" src="/images/flags/texas_flag.png" fluid />
                            <span className="label">Texas</span>
                        </Col>
                    </Row>
                </Container>
                {chat}
            </div>
        );
    }
}

export default Home;
