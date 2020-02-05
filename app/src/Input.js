import React from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import './Input.css';

class Input extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            message: ""
        };


        this.handleChange = this.handleChange.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.handleKeyUp = this.handleKeyUp.bind(this);
    }

    render() {
        return (
            <div className="Input">
                <Form inline>
                    <Form.Control as="input" onChange={this.handleChange} onKeyUp={this.handleKeyUp} value={this.state.message} placeholder="Your question" size="sm" className="mr-sm-2" />
                    <Button as="input" type="button" value="Send" onClick={this.handleClick} size="sm" onChange={this.handleClick} />
                </Form>
            </div>
        );
    }

    handleKeyUp(e) {
        if (e.key === 'Enter') {
            this.handleClick(e);
        }
    }

    handleClick(e) {
        e.preventDefault();
        this.props.onMessage(this.state.message);
        this.setState({ message: '' });
    }

    handleChange(e) {
        this.setState({ message: e.target.value });
    }
}

export default Input;
