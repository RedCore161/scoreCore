import { Button, Col } from "react-bootstrap";
import { authCheckState, logout } from "../../store/actions/auth";
import React from "react";

const Navbar = () => {

  const isAdmin = localStorage.getItem("is_staff")

  return (
    <Col md={ 2 } id={ "main-Navbar" }>
      <Button variant="primary" className="w-100 mt-2" size="lg" onClick={ () => {
        logout();
        window.location.reload();
      } }>Logout</Button>
      <Button href="/project/overview/" variant="info" className="w-100 mt-2" size="lg">Projects</Button>
      { isAdmin === "true" && (
        <>
          <Button href="/project/evaluate/" variant="info" className="w-100 mt-2" size="lg">Evaluate</Button>
          <Button href="/project/backup/" variant="info" className="w-100 mt-2" size="lg">Backup</Button>
          <Button href="/docker/" variant="info" className="w-100 mt-2" size="lg">Docker Status</Button>
          <Button href={`${process.env.REACT_APP_BACKEND_URL}/admin`} variant="primary" className="w-100 mt-2" size="lg">Admin</Button>
        </>
      ) }

    </Col>
  );
};

export default Navbar;
