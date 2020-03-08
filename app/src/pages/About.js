import React from 'react';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Image from 'react-bootstrap/Image';
import Row from 'react-bootstrap/Row';
import './About.css';

class About extends React.Component {
    render() {
        return (
            <Container>
                <h1>About</h1>
                <h2>The Team</h2>
                <Row className="gallery">
                    <Col>
                        <Image alt="Shane Andrade" src="/images/team/shane.jpg" roundedCircle fluid />
                        <span class="label">Shane Andrade</span>
                    </Col>
                    <Col>
                        <Image alt="Maria Corina Cabezas " src="/images/team/anonf.jpg" roundedCircle fluid />
                        <span class="label">Maria Corina Cabezas</span>
                    </Col>
                    <Col>
                        <Image alt="Ivan Fan" src="/images/team/anonm.jpg" roundedCircle fluid />
                        <span class="label">Ivan Fan</span>
                    </Col>
                    <Col>
                        <Image alt="Yuchen Zhang" src="/images/team/anonf.jpg" roundedCircle fluid />
                        <span class="label">Yuchen Zhang</span>
                    </Col>
                </Row>

                <h2>Our Mission</h2>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            </Container>
        );
    }
};

export default About;
