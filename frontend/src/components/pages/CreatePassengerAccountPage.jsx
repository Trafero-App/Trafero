import {useContext, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import TextboxWithToggleVisibility from '../TextboxWithToggleVisibility';
import { MapContext } from '../../App';
import { ClipLoader } from 'react-spinners';

const isValidName = (name) => {
    const nameRegex = /^[a-zA-Z]+([ '-][a-zA-Z]+)*$/;
    return nameRegex.test(name);
}

//format is YYYY-MM-DD
const getCurrentDate = () => {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const day = String(date.getDate()).padStart(2,'0');
    return `${year}-${month}-${day}`;
}
const isValidDate= (dateString) => {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    return regex.test(dateString);
}
const isAgeDifferenceAtLeast18Years = (dateString1, dateString2) => {
    // Helper function to check if a string is a valid YYYY-MM-DD date
    function isValidDate(dateString) {
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateRegex.test(dateString)) return false;
  
      const dateParts = dateString.split('-');
      const year = parseInt(dateParts[0], 10);
      const month = parseInt(dateParts[1], 10) - 1; // Months are 0-indexed
      const day = parseInt(dateParts[2], 10);
  
      const date = new Date(year, month, day);
      return date.getFullYear() === year && date.getMonth() === month && date.getDate() === day;
    }
  
    if (!isValidDate(dateString1) || !isValidDate(dateString2)) {
      return false; // Invalid date format
    }
  
    const date1 = new Date(dateString1);
    const date2 = new Date(dateString2);
  
    // Calculate age difference in milliseconds
    const ageDifferenceMillis = Math.abs(date2 - date1);
  
    // Convert milliseconds to years (approximation)
    const ageDifferenceYears = ageDifferenceMillis / (1000 * 60 * 60 * 24 * 365.25);
  
    return ageDifferenceYears >= 18;
}

const isValidEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

const isValidPhoneNumber = (str) => {
    const eightDigitsRegex = /^\d{8}$/;
    return eightDigitsRegex.test(str);
}

const isValidPassword = (password) => {
    //checks if password is at least 8 characters long, has at least 1 uppercase letter, 1 lowercase letter and 1 number
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return passwordRegex.test(password);
}

const CreatePassengerAccountPage = () => {

    const value = useContext(MapContext)
    const {setAuthenticationToken, setLoggedIn, setUserType} = value

    const navigate = useNavigate()

    const [isLoading, setLoading] = useState(false)

    const [firstName,setFirstName] = useState('')
    const [lastName,setLastName] = useState('')
    const [birthday, setBirthday] = useState('')
    const [email,setEmail] = useState('')
    const [phoneNumber,setPhoneNumber] =useState('')
    const [password,setPassword] = useState('')
    const [passwordVisible, setPasswordVisible] = useState(false);
    const [repeatedPassword,setRepeatedPassword] = useState('');

    const [message1, setMessage1] = useState('')
    const [message2, setMessage2] = useState('')
    const [message3, setMessage3] = useState('')
    const [message4, setMessage4] = useState('')

    const isUsedEmail = async (email) => {
        var result
        await axios({
            method: 'get',
            url: `/api/check_email?email=${email}`,
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then((res) => {
            result=!res.data.is_valid
        })
        .catch(() =>  {result=true})
        return result
    }
    const isUsedPhoneNumber = async (phoneNumber) => {
        var result
        await axios({
            method: 'get',
            url: `/api/check_phone_number?phone_number=${phoneNumber}`,
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then((res) => {
            result=!res.data.is_valid
        })
        .catch(() =>  {result=true})
        return result
    }

    const createPassengerAccount = async () => {
        const formData = new FormData()
        formData.append('account_type','passenger')
        formData.append('first_name',firstName)
        formData.append('last_name', lastName)
        formData.append('date_of_birth',birthday)
        if(phoneNumber!='') formData.append('phone_number',phoneNumber)
        if(email!='') formData.append('email', email)
        formData.append('password',password)
        await axios({
            url: '/api/signup',
            method: 'post',
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            data: formData
        })
        .then((res) => {
            if(res.status==200){
                setUserType('passenger')
                setAuthenticationToken(res.data.token.access_token)
                localStorage.setItem('authentication-token',res.data.token.access_token)
                setLoggedIn(true)
                navigate('/map')
                window.location.reload()
            }
        })
        .catch((e) => {
            //409 if already used email or phone number, 422 invalid input
            setLoading(false)
        })
    }

    const handleCreateAccountClick = async (e) => {
        e.preventDefault()
        if(isLoading) return
        setLoading(true)
        //remove all messages
        setMessage1('')
        setMessage2('')
        setMessage3('')
        setMessage4('')
        var allGood=true
        //check for empty fields
        if(firstName=='' && lastName==''){
            allGood=false
            setMessage1('Please enter your first name and last name')
        }
        else if(firstName==''){
            allGood=false
            setMessage1('Please enter your first name')
        }
        else if(lastName==''){
            allGood=false
            setMessage1('Please enter your last name')
        }
        if(birthday==''){
            allGood=false
            setMessage2('Please enter your birthday')
        }
        if(phoneNumber=='' && email==''){
            allGood=false
            setMessage3('Please enter your email or phone number')
        }
        if(password=='' && repeatedPassword==''){
            allGood=false
            setMessage4('Please enter your password')
        }
        else if(password==''){
            allGood=false
            setMessage4('Please enter your password')
        }
        else if(repeatedPassword==''){
            allGood=false
            setMessage4('Please repeat your password')
        }

        //checks for valid first and last name
        if(!isValidName(firstName) && firstName!='' && !isValidName(lastName) && lastName!=''){
            allGood=false
            setMessage1('First name and last name are invalid')
        }
        else if(!isValidName(firstName) && firstName!=''){
            allGood=false
            setMessage1('First name is invalid')
        }
        else if(!isValidName(lastName) && lastName!=''){
            allGood=false
            setMessage1('Last name is invalid')
        }

        //checks for invalid birthday
        if(!isValidDate(birthday) && birthday!=''){
            allGood=false
            setMessage2('Birthday is invalid')
        }
        else if(!isAgeDifferenceAtLeast18Years(birthday, getCurrentDate()) && birthday!=''){
            allGood=false
            setMessage2('You must at least 18 years old')
        }

        //check for invalid email or phone number
        if(!isValidEmail(email) && email!='' && !isValidPhoneNumber(phoneNumber) && phoneNumber!=''){
            allGood=false
            setMessage3('Email and phone number are invalid')
        }
        else if(!isValidEmail(email) && email!=''){
            allGood=false
            setMessage3('Email is invalid')
        }
        else if(!isValidPhoneNumber(phoneNumber) && phoneNumber!=''){
            allGood=false
            setMessage3('Phone number is invalid')
        }
        else{
            const usedEmail = await isUsedEmail(email)
            const usedPhoneNumber = await isUsedPhoneNumber(phoneNumber)
            if(usedEmail && usedPhoneNumber && phoneNumber!='' && email!=''){
                allGood=false
                setMessage3('Email and phone number are already used')
            }
            else if(usedEmail && email!=''){
                allGood=false
                setMessage3('That email is already used')
            }
            else if(usedPhoneNumber && phoneNumber!=''){
                allGood=false
                setMessage3('That phone number is already used')
            }
        }

        //checks for invalid password and repeated password
        if(password!=repeatedPassword!='' && password!=''){
            allGood=false
            setMessage4("Passwords don't match")
        }
        else if(!isValidPassword(password) && password!=''){
            allGood=false
            setMessage4('Password must contain at least 8 characters, 1 lowercase letter, 1 uppercase letter and 1 number')
        }

        if(allGood){
            createPassengerAccount()
        }
        else{
            setLoading(false)
        }
    }

    return (
        <div className='w-full flex flex-col items-center'>
            <form 
            className="bg-white p-6 rounded-xl shadow-md w-full max-w-96"
            onSubmit={handleCreateAccountClick}
            >
                <div className='flex flex-col items-center mb-6'>
                    <h1 className='font-semibold text-2xl mb-3'>Sign Up for _</h1>
                    <h1>Create a free account or <span className='text-blue3 cursor-pointer' onClick={() => navigate('/sign-in')}>sign in</span></h1>
                </div>
                <input 
                id='first-name-field'
                value={firstName}
                className="mb-3 w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                placeholder="First Name"
                onChange={e => setFirstName(e.target.value)}
                />
                <input 
                id='last-name-field'
                value={lastName}
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                placeholder="Last Name"
                onChange={e => setLastName(e.target.value)}
                />
                <div className='h-6'>
                    {message1 &&
                    <h1 className='text-unavailable-red text-xs mt-1'>{message1}</h1>
                    }
                </div>
                <input
                value={birthday}
                type='date'
                min="1924-01-01" max={getCurrentDate()}
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                onChange={(e) => setBirthday(e.target.value)}
                />
                <div className='h-6'>
                    {message2 &&
                    <h1 className='text-unavailable-red text-xs mt-1'>{message2}</h1>
                    }
                </div>
                <input 
                id='email-field'
                value={email}
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                placeholder="Email Address"
                onChange={e => {setEmail(e.target.value); setMessage2(null)}}
                /> 
                <div className='text-gray2 flex items-center before:flex-1 before:p-px before:m-2 before:bg-gray2 after:flex-1 after:p-px after:m-2 after:bg-gray2'>OR</div>
                <input 
                id='phone-number-field'
                value={phoneNumber}
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                placeholder="Phone Number"
                onChange={e => setPhoneNumber(e.target.value)}
                />
                <div className="h-6">
                    {message3 &&
                    <h1 className='text-unavailable-red text-xs mt-1'>{message3}</h1>
                    }
                </div>
                <TextboxWithToggleVisibility
                className='mb-3'
                password={password}
                setPassword={setPassword}
                passwordVisible={passwordVisible}
                setPasswordVisible={setPasswordVisible}
                />
                <input
                id='repeated-password-field'
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                value={repeatedPassword}
                type='password'
                placeholder='Repeat Password'
                onChange={e => setRepeatedPassword(e.target.value)}
                />    
                <div className='min-h-6'>
                    {message4 &&
                    <h1 className='text-unavailable-red text-xs my-1'>{message4}</h1>
                    }
                </div>
                <button 
                type='submit'
                className="w-full bg-blue3 hover:bg-blue4 transition duration-200 text-white py-2 rounded-xl flex justify-center items-center"
                >
                {isLoading ?
                <ClipLoader color='white' size='24px'/>
                :
                'Create Account'
                }
                </button>
            </form>
        </div>
    )
}

export default CreatePassengerAccountPage