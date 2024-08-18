import React, { useState, useContext } from 'react';
import { MapContext } from '../../App';
import {useNavigate} from 'react-router-dom';
import axios from 'axios'
import TextboxWithToggleVisibility from '../TextboxWithToggleVisibility'
import { ClipLoader } from 'react-spinners';

const isValidEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

const isValidPhoneNumber = (str) => {
  const eightDigitsRegex = /^\d{8}$/;
  return eightDigitsRegex.test(str);
}


const SignInPage = () => {

  const [isLoading, setLoading] = useState(false)

  const value = useContext(MapContext)
  const {setAuthenticationToken, setLoggedIn, setUserType} = value

  const navigate = useNavigate()

  const [emailOrPhoneNumber,setEmailOrPhoneNumber] = useState('')
  const [password,setPassword] = useState('')
  const [signInType, setSignInType] = useState('passenger');
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [success, setSuccess] = useState(false)

  const [message1, setMessage1] = useState('')
  const [message2, setMessage2] = useState('')

  const signInAsPassenger = async () => {
    await axios({
      method: 'post',
      url: '/api/login/passenger',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      data: {
        username: emailOrPhoneNumber,
        password: password,
        grant_type: 'password'
      }
    })
    .then((res) => {
      if(res.status==200){
        setAuthenticationToken(res.data.token.access_token)
        localStorage.setItem('authentication-token',res.data.token.access_token)
        setUserType('passenger')
        setLoggedIn(true)
        setSuccess(true)
        navigate('/map')
        window.location.reload()
      }
    })
    .catch((e) =>  {
      if(e.response.status==422){
        setMessage2('Invalid credentials.')
      }
      if(e.response.status==401){
        if(e.response.data.detail.error_code=='INVALID_CREDENTIALS'){
          setMessage2('Invalid credentials.')
        }
      }
      setLoading(false)
    })
  }

  const signInAsDriver = async () => {
    await axios({
      method: 'post',
      url: '/api/login/driver',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      data: {
        username: emailOrPhoneNumber,
        password: password,
        grant_type: 'password'
      }
    })
    .then((res) => {
      if(res.status==200){
        setAuthenticationToken(res.data.token.access_token)
        localStorage.setItem('authentication-token',res.data.token.access_token)
        setUserType('driver')
        setSuccess(true)
        setLoggedIn(true)
        navigate('/map')
        window.location.reload()
      }
    })
    .catch((e) =>  {
      if(e.response.status==422){
        setMessage2('Invalid credentials.')
      }
      if(e.response.status==401){
        if(e.response.data.detail.error_code=='INVALID_CREDENTIALS'){
          setMessage2('Invalid credentials.')
        }
      }
      setLoading(false)
    })
  }

  const handleSignInButton = (e) => {
    e.preventDefault()
    if(isLoading) return;
    setLoading(true)
    setMessage1('')
    setMessage2('')
    var allGood = true
    if(emailOrPhoneNumber==''){
      allGood = false
      setMessage1('Please enter your email or phone number')
    }
    if(password==''){
      allGood = false
      setMessage2('Please enter your password')
    }

    if(emailOrPhoneNumber!='' && !isValidEmail(emailOrPhoneNumber) && !isValidPhoneNumber(emailOrPhoneNumber)){
      allGood = false
      setMessage1('Invalid email or phone number')
    }

    if(allGood){
      if(signInType=='driver'){
        signInAsDriver()
      }
      else{
        signInAsPassenger()
      }
    }
    else{
      setLoading(false)
    }
  }

  return (
    <div className='w-full flex flex-col items-center'>
      <div className='text-white text-3xl font-bold mb-6'>
        <h1>Welcome Back!</h1>
      </div>
      <form 
      className="bg-white p-6 rounded-xl shadow-md w-full max-w-96"
      onSubmit={handleSignInButton}
      >
        <h1 className='flex justify-center mb-4 text-xl font-bold'>I am a ...</h1>
        <div className="flex justify-between mb-6">
          <button
          type='button'//so it doesnt trigger submit function
          className={`w-full h-10 mr-1.5 rounded-xl ${signInType === 'passenger' ? 'bg-blue3 hover:bg-blue4 transition duration-200 text-white' : 'hover:bg-gray1 border-2 border-gray1'} transition duration-200`}
          onClick={() => {
            setSignInType('passenger')
            setEmailOrPhoneNumber('')
            setPassword('')
          }}
          >
            Passenger
          </button>
          <button
          type='button'
          className={`w-full h-10 ml-1.5 rounded-xl ${signInType === 'driver' ? 'bg-blue3 hover:bg-blue4 transition duration-200 text-white' : 'hover:bg-gray1 border-2 border-gray1'} transition duration-200`}
          onClick={() => {
            setSignInType('driver')
            setEmailOrPhoneNumber('')
            setPassword('')
          }}
          >
            Driver
          </button>
        </div>
        <input 
        id='email-phonenumber-field'
        value={emailOrPhoneNumber}
        className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
        placeholder="Email or Phone Number"
        onChange={e => setEmailOrPhoneNumber(e.target.value)}
        />
        <div className='min-h-3'>
        <h1 className='text-unavailable-red text-xs my-1'>{message1}</h1>
        </div>
        <TextboxWithToggleVisibility
        password={password}
        setPassword={setPassword}
        passwordVisible={passwordVisible}
        setPasswordVisible={setPasswordVisible}
        />
        <div className='min-h-3'>
        <h1 className='text-unavailable-red text-xs my-1'>{message2}</h1>
        </div>
        
        <div className='flex justify-center '>
          <button 
          type='button'
          className="underline mb-1 text-xs">
            Forgot Password?
          </button>
        </div>
        <button 
        type='submit'
        className="w-full flex justify-center items-center bg-blue3 hover:bg-blue4 transition duration-200 text-white py-2 rounded-xl mt-4"
        >
        {isLoading ?
        <ClipLoader color='white' size='24px'/>
        :
        'Sign in'
        }
        </button>
        <div className='flex text-sm mt-2'>
          {success ?
          <h1 className='text-blue3'>Successfully logged in, redirecting to map</h1>
          :
          <h1>Don't have an account? 
          <span
          className="text-blue3 cursor-pointer"
          onClick={() => {
            if(signInType=='passenger'){
              navigate('/sign-in/create-passenger-account')
            }
            else{
              navigate('/sign-in/create-driver-account')
            }
          }}
          >
            {" Register here"}
          </span>
          </h1>
          }
        </div> 
      </form>
    </div>
  );
};

export default SignInPage;