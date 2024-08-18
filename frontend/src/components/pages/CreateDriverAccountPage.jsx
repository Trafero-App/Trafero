import {useState, useEffect, useContext} from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import TextboxWithToggleVisibility from '../TextboxWithToggleVisibility';
import { MapContext } from '../../App';
import SelectedRouteItem from '../sign in components/SelectedRouteItem';
import { ClipLoader } from 'react-spinners';
import SearchedRouteItem from '../sign in components/SearchedRouteItem';

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
      const year = parseInt(dateParts[0],   
   10);
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

const isValidLicensePlate = (str) => {
    const regex = /^[A-Z] \d{1,7}$/;
    return regex.test(str);
}

const extension = (file) => {
    const fileName = file.name;
    const lastDotIndex = fileName.lastIndexOf('.');

    if (lastDotIndex !== -1) {
        return fileName.substring(lastDotIndex + 1);
    } else {
        return ''; // No extension found
    }
}

const useDebounce = (value,delay) => {// TODO : understand wtf this is
    const [debouncedSearchTerm,setDebouncedSearchTerm] = useState('')
    useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedSearchTerm(value)
      }, delay)
  
      return () => {
        clearTimeout(handler)
      }
    },[value,delay]) 
    return debouncedSearchTerm
  }

const CreateDriverAccountPage = () => {

    const [isLoading, setLoading] = useState(false)

    const value = useContext(MapContext)

    const carBrands = [
        "Toyota",
        "Honda",
        "Ford",
        "Chevrolet",
        "Nissan",
        "Hyundai",
        "Kia",
        "Volkswagen",
        "Mazda",
        "Subaru",
        "Jeep",
        "Ram",
        "GMC",
        "Mitsubishi",
        "Fiat",
        "Renault",
        "Peugeot",
        "Citroen",
        "Opel",
        "Skoda",
        "Dacia",
        "Suzuki",
        "Fiat Chrysler Automobiles (FCA)",
        "BMW",
        "Mercedes-Benz",
        "Audi",
        "Lexus",
        "Porsche",
        "Volvo",
        "Jaguar",
        "Land Rover",
        "Infiniti",
        "Acura",
        "Cadillac",
        "Lincoln",
        "Alfa Romeo",
        "Maserati",
        "Genesis",
        "Tesla",
        "BYD",
        "NIO",
        "Polestar",
        "Rivian",
        "Lucid",
        "VinFast",
        "MG",
        "Geely",
        "Great Wall Motors",
        "Xpeng",
        "Aiways",
        "Ferrari",
        "Lamborghini",
        "Bentley",
        "Rolls-Royce",
        "Aston Martin",
        "McLaren",
        "Lotus",
        "Bugatti",
        "Koenigsegg",
        "Pagani",
        "Rimac",
        "Fisker",
        "Lucid",
        "Faraday Future",
        "Canoo",
        "Sono Motors",
        "Atlis Motor",
        "Lordstown Motors",
        "Nikola Motor"
    ];

    const navigate = useNavigate()

    const [firstName,setFirstName] = useState('')
    const [lastName,setLastName] = useState('')
    const [birthday, setBirthday] = useState('')
    const [email,setEmail] = useState('')
    const [phoneNumber,setPhoneNumber] =useState('')
    const [password,setPassword] = useState('')
    const [passwordVisible, setPasswordVisible] = useState(false);
    const [repeatedPassword,setRepeatedPassword] = useState('');

    const [vehicleType, setVehicleType] = useState('')
    const [vehicleBrand, setVehicleBrand] = useState('')
    const [vehicleModel, setVehicleModel] = useState('')
    const [vehicleColor, setVehicleColor] = useState('')
    const [licensePlate, setLicensePlate] = useState('')
    const [driversLicense, setDriversLicense] = useState('')
    const [vehicleRegistration, setVehicleRegistration] = useState('')

    const [message1, setMessage1] = useState('')
    const [message2, setMessage2] = useState('')
    const [message3, setMessage3] = useState('')
    const [message4, setMessage4] = useState('')
    const [message5, setMessage5] = useState('')
    const [message6, setMessage6] = useState('')
    const [message7, setMessage7] = useState('')
    const [message8, setMessage8] = useState('')
    const [message9, setMessage9] = useState('')
    const [message10, setMessage10] = useState('')

    const [step, setStep] = useState(1)

    const [searchTerm, setSearchTerm] = useState('')
    const debouncedSearchTerm = useDebounce(searchTerm, 350)
    const [isLoadingSearch, setLoadingSearch] = useState(false)
    const [searchData, setSearchData] = useState(null)
    const {routes, setRoutes, setLoggedIn, setAuthenticationToken, setUserType} = value

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
    const isUsedLicensePlate = async (licensePlate) => {
        var result
        await axios({
            method: 'get',
            url: `/api/check_license_plate?license_plate=${licensePlate}`,
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

    const fetchRoutes = async (query) => {
        await axios.get(`/api/search_routes/${query}`,{
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then((res) => {
            if(res.status==200){
                setSearchData(res.data.routes)
                setLoadingSearch(false)
            }
        })
        .catch((e) => {
            setSearchData([])
            setLoadingSearch(false)
        })
    }
    useEffect(() => {
        if(debouncedSearchTerm==''){
            setSearchData(null)
            setLoading(false)
        }
        else{
            fetchRoutes(debouncedSearchTerm)
        }
    },[debouncedSearchTerm])

    const createDriverAccount = async () => {
        const formData = new FormData()
        formData.append('account_type','driver')
        formData.append('first_name',firstName)
        formData.append('last_name', lastName)
        formData.append('date_of_birth',birthday)
        formData.append('phone_number',phoneNumber)
        if(email!='') formData.append('email', email)
        formData.append('password',password)
        formData.append('vehicle_type',vehicleType)
        formData.append('brand', vehicleBrand)
        formData.append('model', vehicleModel)
        formData.append('license_plate', licensePlate)
        formData.append('vehicle_color', vehicleColor)
        formData.append('routes', JSON.stringify(routes.map((e) => e.route_id)))
        formData.append('vehicle_registration_file', vehicleRegistration)
        formData.append('drivers_license_file', driversLicense)
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
                setUserType('driver')
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

    const handleContinueClick1 = async (e) => {
        e.preventDefault()
        if(isLoading) return
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

        //check for invalid/empty email or phone number
        if(phoneNumber==''){
            allGood=false
            setMessage3("Please enter your phone number")
        }
        else if(!isValidPhoneNumber(phoneNumber)){
            allGood=false
            setMessage3("Phone number is invalid")
        }
        else if(!isValidEmail(email) && email!=''){
            allGood=false
            setMessage3("Email is invalid")
        }
        else{
            const usedEmail = await isUsedEmail(email)
            const usedPhoneNumber = await isUsedPhoneNumber(phoneNumber)
            if(usedEmail && usedPhoneNumber && email!='' && phoneNumber!=''){
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
            setStep(2)
        }
        setLoading(false)
    }
    const handleContinueClick2 = async (e) => {
        e.preventDefault()
        if(isLoading) return
        setMessage5('')
        setMessage6('')
        setMessage7('')
        setMessage8('')
        setMessage9('')
        var allGood = true
        //checks for empty fields
        if(vehicleType==''){
            allGood=false
            setMessage5('Please enter vehicle type')
        }
        if(vehicleBrand==''){
            allGood=false
            setMessage6('Please enter vehicle brand')
        }
        if(vehicleModel=='' && vehicleColor==''){
            allGood=false
            setMessage7('Please enter vehicle model, year & color')
        }
        else if(vehicleModel==''){
            allGood=false
            setMessage7('Please enter vehicle model & year')
        }
        else if(vehicleColor==''){
            allGood=false
            setMessage7('Please enter vehicle color')
        }
        if(licensePlate==''){
            allGood=false
            setMessage8('Please enter your license plate')
        }
        if(driversLicense=='' && vehicleRegistration==''){
            allGood=false
            setMessage9("Please upload your driver's license and vehicle's registration")
        }
        else if(driversLicense==''){
            allGood=false
            setMessage9("Please upload your driver's license")
        }
        else if(vehicleRegistration==''){
            allGood=false
            setMessage9("Please upload your vehicle's registration")
        }

        //checks for invalid input
        if(vehicleType!='' && vehicleType!='van' && vehicleType!='bus'){
            allGood=false
            setMessage5('Invalid vehicle type')
        }
        if(vehicleBrand!='' && !carBrands.includes(vehicleBrand)){
            allGood=false
            setMessage6('Invalid vehicle brand')
        }
        if(licensePlate!='' && !isValidLicensePlate(licensePlate)){
            allGood=false
            setMessage8('Invalid license plate')
        }
        else{
            const usedLicensePlate = await isUsedLicensePlate(licensePlate)
            if(usedLicensePlate){
                allGood=false
                setMessage8('That license plate is already used')
            }
        }
        if((driversLicense!='' && extension(driversLicense)!='pdf') || (vehicleRegistration!='' && extension(vehicleRegistration)!='pdf')){
            allGood=false
            setMessage9('Uploaded files must have the extension .pdf')
        }

        if(allGood){
            setStep(3)
        }
        setLoading(false)
    }
    const handleCreateAccountClick = () => {
        if(routes.length==0){
            setMessage10('You have to choose at least one route before proceeding')
        }
        else{
            setLoading(true)
            createDriverAccount()
        }
    }

    return (
        <div className='w-full flex justify-center'>
        {
        step==1 ?
        <form 
        onSubmit={handleContinueClick1}
        className="bg-white p-6 rounded-xl shadow-md w-full max-w-96">
            <div className='flex flex-col items-center mb-6'>
                <h1 className='font-semibold text-2xl mb-3'>Sign Up for _</h1>
                <h1>Register as a driver or <span className='text-blue3 cursor-pointer' onClick={() => navigate('/sign-in')}>sign in</span></h1>
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
                <h1 className='text-unavailable-red text-xs mt-1'>{message1}</h1>
            </div>
            <input
            value={birthday}
            type='date'
            min="1924-01-01" max={getCurrentDate()}
            className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
            onChange={(e) => setBirthday(e.target.value)}
            />
            <div className='h-6'>
                <h1 className='text-unavailable-red text-xs mt-1'>{message2}</h1>
            </div>
            <input 
            id='phone-number-field'
            value={phoneNumber}
            className="mb-3 w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
            placeholder="Phone Number"
            onChange={e => setPhoneNumber(e.target.value)}
            />
            <input 
            id='email-field'
            value={email}
            className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
            placeholder="Email Address (Optional)"
            onChange={e => {setEmail(e.target.value); setMessage2(null)}}
            /> 
            <div className="h-6">
                <h1 className='text-unavailable-red text-xs mt-1'>{message3}</h1>
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
                <h1 className='text-unavailable-red text-xs my-1'>{message4}</h1>
            </div>
            <button 
            type='submit'
            className="w-full flex justify-center items-center bg-blue3 text-white py-2 rounded-xl"
            >
            {isLoading ?
            <ClipLoader color='white' size='24px'/>
            :
            'Continue'
            }
            </button>
        </form>
        :
        step==2 ?
        <form
        className="bg-white rounded-xl shadow-md w-full max-w-96"
        onSubmit={handleContinueClick2}
        >
            <div className='flex flex-col items-center mt-6 mb-3'>
                <h1 className='font-semibold text-2xl mb-3'>Vehicle Info</h1>
            </div>
            <div className='p-6 pt-0'>
                <div
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4"
                >
                    <select 
                    id='vehicle-type-picker'
                    className="w-full rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                    value={vehicleType} 
                    onChange={(e) => setVehicleType(e.target.value)}>
                        <option value="">Vehicle Type (None)</option>
                        <option value="van">Van</option>
                        <option value="bus">Bus</option>
                    </select>
                </div>
                <div className='h-6'>
                    <h1 className='text-unavailable-red text-xs mt-1'>{message5}</h1>
                </div>
                <div
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4"
                >
                    <select 
                    id='vehicle-brand-picker'
                    className="w-full rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                    value={vehicleBrand} 
                    onChange={(e) => setVehicleBrand(e.target.value)}>
                        <option value="">Vehicle Brand (None)</option>
                        {carBrands.map((brand,i) => 
                        <option key={i} value={brand}>{brand}</option>
                        )}
                    </select>
                </div>
                <div className='h-6'>
                    <h1 className='text-unavailable-red text-xs mt-1'>{message6}</h1>
                </div>
                <input
                id='vehicle-model-field'
                value={vehicleModel}
                className="mb-3 w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                placeholder="Vehicle model & year"
                onChange={(e) => setVehicleModel(e.target.value)}
                />
                <input
                id='vehicle-color-field'
                value={vehicleColor}
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                placeholder="Vehicle Color"
                onChange={(e) => setVehicleColor(e.target.value)}
                />
                <div className='h-6'>
                    <h1 className='text-unavailable-red text-xs mt-1'>{message7}</h1>
                </div>
                <input
                id='license-plate-field'
                value={licensePlate}
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                placeholder="License plate"
                onChange={(e) => {
                    //forces white space after first character
                    const newValue = e.target.value
                    const formattedValue = newValue.length==0 ? '' : (newValue.length==1 ? (newValue==' ' ? '': licensePlate.length==2 ? '' : newValue+" ") : newValue)
                    setLicensePlate(formattedValue)
                }}
                />
                <div className='h-6'>
                    <h1 className='text-unavailable-red text-xs mt-1'>{message8}</h1>
                </div>
                <h1 className='pb-2 font-semibold'>Driver's License:</h1>
                <input
                type='file'
                className='mb-3 file:h-10 file:bg-white file:px-6 file:mr-3 file:cursor-pointer file:hover:bg-gray1 file:transition file:duration-200 file:rounded-xl file:border-gray1 file:border-2 file:border-solid w-full'
                onChange={(e) => setDriversLicense(e.target.files[0])}
                />
                <h1 className='pb-2 font-semibold'>Vehicle Registration:</h1>
                <input
                type='file'
                className='file:h-10 file:bg-white file:px-6 file:mr-3 file:cursor-pointer file:hover:bg-gray1 file:transition file:duration-200 file:rounded-xl file:border-gray1 file:border-2 file:border-solid w-full'
                onChange={(e) => setVehicleRegistration(e.target.files[0])}
                />
                <div className='min-h-6'>
                    <h1 className='text-unavailable-red text-xs my-1'>{message9}</h1>
                </div>
                <button 
                type='submit'
                className="w-full flex justify-center items-center bg-blue3 text-white py-2 rounded-xl"
                >
                {isLoading ?
                <ClipLoader color='white' size='24px'/>
                :
                'Continue'
                }
                </button>
            </div>
        </form>
        :
        <div className="bg-white rounded-xl shadow-md w-full max-w-96">
            <div className='flex flex-col items-center mt-6 mb-3'>
                <h1 className='font-semibold text-2xl mb-3'>Choose a Route</h1>
            </div>
            <div className='px-6 pb-6'>
                <h1 className='font-semibold pb-3'>For the last step, please add at least one route to the list of routes that you will be operating on. (This list can be changed later on)</h1>
                <input
                id='route-search-bar'
                value={searchTerm}
                className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                placeholder='Search for routes'
                onChange={(e) => {
                    setLoadingSearch(true)
                    setSearchData(false)
                    setSearchTerm(e.target.value)
                }}
                />
            </div>
            <div className='h-48 w-full scrollable overflow-auto'>
                {searchTerm=='' ?
                //not searching, show what he's chosen so far
                (routes.length==0
                ?
                <div className='w-full h-full flex justify-center items-center'>
                    <h1 className='font-semibold'>No routes have been chosen yet</h1>
                </div>
                :
                routes.map((e,i) => <SelectedRouteItem key={i} routeData={e}/>)
                )
                :
                (!searchData || isLoadingSearch ?
                <div className='w-full h-full flex justify-center items-center'>
                    <ClipLoader size='29px' color='#C8C8C8'/>
                </div>
                :
                searchData.map((e,i) => <SearchedRouteItem key={i} routeData={e}/>)
                )
                }
            </div>
            <div className='min-h-6 px-6'>
                <h1 className='text-unavailable-red text-xs my-1'>{message10}</h1>
            </div>
            <div className='p-6 pt-0'>
                <button 
                className=" flex justify-center items-center w-full bg-blue3 text-white py-2 rounded-xl"
                onClick={handleCreateAccountClick}
                >
                {isLoading ?
                <ClipLoader color='white' size='24px'/>
                :
                'Create Account'
                }
                </button>
            </div>
            
        </div>
        }
        </div>
    )
}

export default CreateDriverAccountPage