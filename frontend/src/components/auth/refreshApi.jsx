import axios from "axios"
import createRefresh from "react-auth-kit/createRefresh";
const intervalMin = 5

const refreshApi = createRefresh({
  interval: intervalMin,   // Refreshs the token in every 10 minutes
  refreshApiCallback: async (
    {   // arguments
      authToken,
      authTokenExpireAt,
      refreshToken,
      refreshTokenExpiresAt,
      authUserState
    }) => {
    try {
      const response = await axios.post(`${ process.env.REACT_APP_BACKEND_URL }/api/token/refresh/`, {"refresh": refreshToken}, {
        headers: {"Authorization": `Bearer ${authToken}`}}
      )
      console.log("refreshApi", authTokenExpireAt, refreshTokenExpiresAt);
      return {
        isSuccess: true,
        newAuthToken: response.data.access,
        newAuthTokenExpireIn: intervalMin,
        newRefreshTokenExpiresIn: 60,
        newRefreshToken: response.data.refresh,
        newAuthUserState: authUserState,
      }
    }
    catch(error){
      console.error(error)
      return {
        isSuccess: false
      }
    }
  }
})
export default refreshApi
