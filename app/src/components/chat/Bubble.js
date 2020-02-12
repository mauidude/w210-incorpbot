import React from 'react';
import './Bubble.css';

class Bubble extends React.Component {
    render() {
        return <div className={"Bubble " + (this.props.sender === "me" ? "Bubble-me" : "Bubble-you")}>{this.props.message}</div>
    }
}

export default Bubble;
