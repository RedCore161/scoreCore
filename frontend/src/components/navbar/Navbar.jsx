import { Button, Col } from "react-bootstrap";
import React from "react";
import { useAuthUser, useSignOut } from "react-auth-kit";
import { useNavigate } from "react-router";
import { useLocation } from "react-router-dom";

const Navbar = ({ content, act }) => {

  const singOut = useSignOut();
  const navigate = useNavigate();
  const location = useLocation();
  const _auth = useAuthUser();
  const auth = _auth();

  const logout = () => {
    singOut();
    navigate(`/login?forward=${ location.pathname }`);
  };

  return (
    <>
      <Col md={ 2 } id={ "main-Navbar" } className={" mt-4"}>
        <Button href="/project/overview/" variant="info" className="w-100" size="lg">Projects</Button>
        { auth?.is_superuser && (
          <>
            <Button href="/project/evaluate/" variant={ act === "evaluate" ? "info" : "primary" }  className="w-100 mt-2" size="lg">Evaluate</Button>
            <Button href="/project/backup/" variant={ act === "backup" ? "info" : "primary" }  className="w-100 mt-2" size="lg">Backup</Button>
            <Button href="/docker/" variant={ act === "docker" ? "info" : "primary" }  className="w-100 mt-2" size="lg">Docker Status</Button>
            <Button href={`${process.env.REACT_APP_BACKEND_URL}/admin`} variant="primary" className="w-100 mt-2" size="lg">Admin</Button>
          </>
        ) }
        <Button variant="primary" className="w-100 mt-2" size="lg" onClick={ () => {
          logout();
          window.location.reload();
        } }>Logout</Button>
      </Col>
      <Col md={ 10 } className={ `ps-3` }>
        { content }
      </Col>
    </>
  );
};

export default Navbar;
