import { createBrowserHistory } from 'history';
import React from 'react';
import ReactGA from 'react-ga';
import { Route, Router, Switch } from 'react-router-dom';
import Footer from './components/Footer';
import Header from './components/Header';
import About from './pages/About';
import Home from './pages/Home';


const history = createBrowserHistory();
let unlisten = history.listen(location => {
  ReactGA.set({ page: location.pathname });
  ReactGA.pageview(location.pathname);
});

class App extends React.Component {
  constructor(props) {
    super(props);

    ReactGA.initialize(this.props.ga,
      {
        debug: this.props.ga_debug,
        gaOptions: { siteSpeedSampleRate: 1.0 }
      }
    );
  }

  componentDidMount() {
    // initial page view
    ReactGA.pageview(window.location.pathname + window.location.search);
  }

  componentWillUnmount() {
    unlisten();
  }

  render() {
    return (
      <Router history={history}>
        <Header />
        <Switch>
          <Route path="/about">
            <About />
          </Route>
          <Route path="/">
            <Home server={this.props.server} />
          </Route>
        </Switch>
        <Footer />
      </Router>
    )
  }
}

export default App;
