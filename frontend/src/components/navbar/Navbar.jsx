import { Button, Col } from "react-bootstrap";
import React from "react";
import { useAuthUser, useSignOut } from "react-auth-kit";
import { useNavigate } from "react-router";
import { useLocation } from "react-router-dom";

const Navbar = () => {

  const singOut = useSignOut();
  const navigate = useNavigate();
  const location = useLocation();
  const auth = useAuthUser();
  const isAuth = auth()

  const logout = () => {
    singOut();
    navigate(`/login?forward=${ location.pathname }`);
  };

  return (
    <Col md={ 2 } id={ "main-Navbar" }>
      <Button variant="primary" className="w-100 mt-4" size="lg" onClick={ () => {
        logout();
        window.location.reload();
      } }>Logout</Button>
      <Button href="/project/overview/" variant="info" className="w-100 mt-2" size="lg">Projects</Button>
      { isAuth.is_superuser && (
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
