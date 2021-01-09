import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Grid, Typography, TextField, Button } from "@material-ui/core";

export default class RoomJoinPage extends Component {
	defaultVotes = 2;

	constructor(props) {
		super(props);

		this.state = {
			roomCode: "",
			error: "",
		};
	}

	handleEnterRoomPressed = (e) => {
		const requestOptions = {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				code: this.state.roomCode,
			}),
		};

		fetch("/api/join-room", requestOptions)
			.then((response) => {
				if (response.ok) {
					this.props.history.push(`/room/${this.state.roomCode}`);
				} else {
					this.setState({
						error: "Room not found.",
					});
				}
			})
			.catch((error) => console.log(error));
	};

	handleTextFieldChange = (e) => {
		this.setState({
			roomCode: e.target.value,
		});
	};

	render() {
		return (
			<Grid container spacing={1} alignItems="center">
				<Grid item xs={12} align="center">
					<Typography component="h4" variant="h4">
						{" "}
						Join a Room
					</Typography>
				</Grid>
				<Grid item xs={12} align="center">
					<TextField
						error={this.state.error}
						label="Code"
						placeholder="Enter a room code"
						value={this.state.roomCode}
						helperText={this.state.error}
						variant="outlined"
						onChange={this.handleTextFieldChange}
					/>
				</Grid>
				<Grid item xs={12} align="center">
					<Button
						variant="contained"
						color="primary"
						onClick={this.handleEnterRoomPressed}
					>
						Enter Room
					</Button>
				</Grid>
				<Grid item xs={12} align="center">
					<Button
						variant="contained"
						color="secondary"
						to="/"
						component={Link}
					>
						Back
					</Button>
				</Grid>
			</Grid>
		);
	}
}