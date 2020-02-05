import React from 'react';
import Bubble from './Bubble';
import './History.css';
import PendingBubble from './PendingBubble';

class History extends React.Component {
    constructor(props) {
        super(props);

        this.history = React.createRef();
    }

    componentDidMount() {
        this.scrollToBottom();
    }

    componentDidUpdate() {
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.history.current.scrollTop = this.history.current.scrollHeight;
    }

    render() {
        if (this.props.pending) {
            var pending = <PendingBubble />;
        }

        return (
            <div className="History" ref={this.history}>
                {this.props.dialog.map((item, key) => <Bubble key={key} message={item.message} sender={item.sender} />)}
                {pending}
            </div >
        );
    }
}

export default History;
