import React, { Component } from "react";
import CreateRoomPage from "./CreateRoomPage";
import { Grid, Button, Typography } from "@material-ui/core";
import MusicPlayer from "./MusicPlayer";

export default class Room extends Component {
	constructor(props) {
		super(props);

		this.state = {
			votesToSkip: 2,
			guestCanPause: false,
			isHost: false,
			showSetting: false,
			isSpotifyAuthenticated: false,
			song: {},
		};

		this.roomCode = this.props.match.params.roomCode;
		this.getRoomDetails();
		this.getCurrentSong();
	}

	authenticateSpotify = () => {
		fetch("/spotify/is-authenticated")
			.then((response) => response.json())
			.then((data) => {
				this.setState({ isSpotifyAuthenticated: data.status });
				if (!data.status) {
					fetch("/spotify/get-auth-url")
						.then((response) => response.json())
						.then((data) => {
							window.location.replace(data.url);
						});
				}
			});
	};

	getRoomDetails = () => {
		fetch("/api/get-room" + "?code=" + this.roomCode)
			.then((response) => {
				if (!response.ok) {
					this.props.leaveRoomCallback();
					this.props.history.push("/");
				} else {
					return response.json();
				}
			})
			.then((data) => {
				this.setState({
					votesToSkip: data.votes_to_skip,
					guestCanPause: data.guest_can_pause,
					isHost: data.is_host,
				});
				if (this.state.isHost) {
					this.authenticateSpotify();
				}
			});
	};

	handleLeaveButtonPressed = () => {
		const requestOptions = {
			method: "POST",
			headers: { "Content-Type": "application/json" },
		};

		fetch("/api/leave-room", requestOptions).then((_response) => {
			this.props.leaveRoomCallback();
			this.props.history.push("/");
		});
	};

	updateShowSettings = (value) => {
		this.setState({
			showSetting: value,
		});
	};

	renderSettingsButton = () => {
		return (
			<Grid item xs={12} align="center">
				<Button
					variant="contained"
					color="primary"
					onClick={() => this.updateShowSettings(true)}
				>
					Settings
				</Button>
			</Grid>
		);
	};

	renderSettings = () => {
		return (
			<Grid container spacing={1}>
				<Grid item xs={12} align="center">
					<CreateRoomPage
						update={true}
						votesToSkip={this.state.votesToSkip}
						guestCanPause={this.state.guestCanPause}
						roomCode={this.roomCode}
						updateCallback={this.getRoomDetails}
					/>
				</Grid>
				<Grid item xs={12} align="center">
					<Button
						variant="contained"
						color="secondary"
						onClick={() => this.updateShowSettings(false)}
					>
						Close
					</Button>
				</Grid>
			</Grid>
		);
	};

	getCurrentSong = () => {
		fetch("/spotify/current-song")
			.then((response) => {
				if (!response.ok) {
					return {};
				} else {
					return response.json();
				}
			})
			.then((data) => this.setState({ song: data }));
	};

	componentDidMount = () => {
		this.interval = setInterval(this.getCurrentSong, 1000);
	};

	componentWillUnmount = () => {
		clearInterval(this.interval);
	};

	render = () => {
		if (this.state.showSetting) {
			return this.renderSettings();
		}
		return (
			<Grid container spacing={1}>
				<Grid item xs={12} align="center">
					<Typography variant="h4" component="h4">
						Code: {this.roomCode}
					</Typography>
				</Grid>
				<MusicPlayer {...this.state.song} />
				{this.state.isHost ? this.renderSettingsButton() : null}
				<Grid item xs={12} align="center">
					<Button
						variant="contained"
						color="secondary"
						onClick={this.handleLeaveButtonPressed}
					>
						Leave Room
					</Button>
				</Grid>
			</Grid>
		);
	};
}
