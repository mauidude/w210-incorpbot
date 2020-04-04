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
                        <Image alt="Ivan Fan" src="/images/team/ivan.jpg" roundedCircle fluid />
                        <span className="label">Ivan Fan</span>
                    </Col>
                    <Col>
                        <Image alt="Shane Andrade" src="/images/team/shane.jpg" roundedCircle fluid />
                        <span className="label">Shane Andrade</span>
                    </Col>
                    <Col>
                        <Image alt="Maria Corina Cabezas " src="/images/team/anonf.jpg" roundedCircle fluid />
                        <span className="label">Maria Corina Cabezas</span>
                    </Col>
                    <Col>
                        <Image alt="Yuchen Zhang" src="/images/team/anonf.jpg" roundedCircle fluid />
                        <span className="label">Yuchen Zhang</span>
                    </Col>
                </Row>

                <h2>Our Mission</h2>
                <p>Our mission is to empower every entrepreneur with access to legal advice for their start up.</p>
            </Container>
        );
    }
};

export default About;
