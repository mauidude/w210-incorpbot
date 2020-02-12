import React from 'react';
import './Bubble.css';

class PendingBubble extends React.Component {
    render() {
        return (
            <div className="PendingBubble">
                <div className="loading">
                    <div className="dot one"></div>
                    <div className="dot two"></div>
                    <div className="dot three"></div>
                </div>
                <div className="tail"></div>
            </div>
        )
    }
};

export default PendingBubble;
