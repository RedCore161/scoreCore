import axios from 'axios';
import { jwtDecode, JwtPayload } from 'jwt-decode';
import React, {
  useContext,
  createContext,
  useState,
  useEffect,
  useCallback,
} from 'react';
import { useLocation, useNavigate } from 'react-router';

type User = JwtPayload;
const intervalMin = 30;

interface AuthCredentials {
  username: string;
  password: string;
}

interface AuthRefresh {
  isSuccess: boolean;
  newAuthToken: string;
  newAuthTokenExpireIn: number;
  newRefreshTokenExpiresIn: number;
}

export interface AuthContextType {
  token: string;
  user: User | null;
  refreshApi: (refreshToken: string) => Promise<AuthRefresh>;
  loginAction: (data: AuthCredentials, forward?: string) => Promise<void>;
  logoutAction: (forward?: string) => void;
  navigate: (url: string) => void;
  location: string;
}

const refreshApi = async (refreshToken) => {
  try {
    const response = await axios.post(
      `${API_URL}/api/token/refresh/`,
      refreshToken,
      {
        headers: { Authorization: `Bearer ${refreshToken}` },
      },
    );

    return {
      isSuccess: true,
      newAuthToken: response.data.token,
      newAuthTokenExpireIn: intervalMin,
      newRefreshTokenExpiresIn: intervalMin * 2,
    } as AuthRefresh;
  } catch (error) {
    console.error(error);
    return {
      isSuccess: false,
    } as AuthRefresh;
  }
};

const defaultAuthContextValue: AuthContextType = {
  token: '',
  user: null,
  refreshApi: (t) => refreshApi(t),
  loginAction: async () => {},
  logoutAction: () => {},
  navigate: () => {},
  location: '/',
};

export const AuthContext = createContext<AuthContextType>(
  defaultAuthContextValue,
);

const API_URL = process.env.REACT_APP_BACKEND_URL ?? '';

const CoreAuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('authToken') || '');
  const [refreshToken, setRefreshToken] = useState(
    localStorage.getItem('refreshToken') || '',
  );
  const [user, setUser] = useState<User | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      try {
        const decoded = jwtDecode<User>(token);
        setUser(decoded);
      } catch (error) {
        console.error('Failed to decode token:', error);
        setUser(null);
      }
    } else {
      setUser(null);
    }
  }, [token]);

  const getCurrentUrl = () => {
    return location.pathname;
  };

  const logoutAction = useCallback(
    async (forward?: string) => {
      try {
        await axios.post(`${API_URL}/api/token/logout/`, {
          refresh: refreshToken,
        });
      } catch (error) {
        console.error(
          'Logout request failed, but proceeding with client-side logout:',
          error,
        );
      } finally {
        setToken('');
        setRefreshToken('');
        localStorage.removeItem('authToken');
        if (forward) {
          navigate(`/login?forward=${encodeURIComponent(forward)}`);
        } else {
          navigate(`/login?forward=${encodeURIComponent(getCurrentUrl())}`);
        }
      }
    },
    [navigate],
  );

  const loginAction = useCallback(
    async (data: AuthCredentials, forward?: string) => {
      try {
        const response = await axios.post(`${API_URL}/api/token/`, data);
        const newToken = response.data.access;
        localStorage.setItem('authToken', newToken);
        setToken(newToken);
        setRefreshToken(response.data.refresh);

        if (forward) {
          navigate(forward);
        } else {
          navigate('/');
        }
      } catch (error) {
        console.error('Login failed:', error);
        await logoutAction(forward);
      }
    },
    [navigate, logoutAction], // depends on logoutAction as it is defined below
  );

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        refreshApi: () => refreshApi(refreshToken),
        loginAction,
        logoutAction,
        navigate,
        location: getCurrentUrl(),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default CoreAuthProvider;

export const useAuth = (): AuthContextType => {
  return useContext(AuthContext);
};
