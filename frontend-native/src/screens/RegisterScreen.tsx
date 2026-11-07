import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ScrollView, Alert, ActivityIndicator,
  KeyboardAvoidingView, Platform, StatusBar,
  Modal, FlatList,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../services/AuthContext';
import { COLORS, SPACING, RADIUS, SHADOWS } from '../utils/theme';

// ──────────────────────────────────────────────
// ALL INDIA STATES & DISTRICTS DATA
// ──────────────────────────────────────────────
const INDIA_STATE_DISTRICT_DATA: { state: string; districts: string[] }[] = [
  { state: 'Andhra Pradesh', districts: ['Anantapur','Chittoor','East Godavari','Guntur','Krishna','Kurnool','Nellore','Prakasam','Srikakulam','Visakhapatnam','Vizianagaram','West Godavari','YSR Kadapa'] },
  { state: 'Arunachal Pradesh', districts: ['Tawang','West Kameng','East Kameng','Papum Pare','Kurung Kumey','Kra Daadi','Lower Subansiri','Upper Subansiri','West Siang','East Siang','Siang','Upper Siang','Lower Siang','Lower Dibang Valley','Dibang Valley','Anjaw','Lohit','Namsai','Changlang','Tirap','Longding'] },
  { state: 'Assam', districts: ['Baksa','Barpeta','Biswanath','Bongaigaon','Cachar','Charaideo','Chirang','Darrang','Dhemaji','Dhubri','Dibrugarh','Goalpara','Golaghat','Hailakandi','Hojai','Jorhat','Kamrup Metropolitan','Kamrup','Karbi Anglong','Karimganj','Kokrajhar','Lakhimpur','Majuli','Morigaon','Nagaon','Nalbari','Dima Hasao','Sivasagar','Sonitpur','South Salmara-Mankachar','Tinsukia','Udalguri','West Karbi Anglong'] },
  { state: 'Bihar', districts: ['Araria','Arwal','Aurangabad','Banka','Begusarai','Bhagalpur','Bhojpur','Buxar','Darbhanga','East Champaran','Gaya','Gopalganj','Jamui','Jehanabad','Kaimur','Katihar','Khagaria','Kishanganj','Lakhisarai','Madhepura','Madhubani','Munger','Muzaffarpur','Nalanda','Nawada','Patna','Purnia','Rohtas','Saharsa','Samastipur','Saran','Sheikhpura','Sheohar','Sitamarhi','Siwan','Supaul','Vaishali','West Champaran'] },
  { state: 'Chandigarh (UT)', districts: ['Chandigarh'] },
  { state: 'Chhattisgarh', districts: ['Balod','Baloda Bazar','Balrampur','Bastar','Bemetara','Bijapur','Bilaspur','Dantewada','Dhamtari','Durg','Gariyaband','Janjgir-Champa','Jashpur','Kabirdham','Kanker','Kondagaon','Korba','Korea','Mahasamund','Mungeli','Narayanpur','Raigarh','Raipur','Rajnandgaon','Sukma','Surajpur','Surguja'] },
  { state: 'Dadra and Nagar Haveli (UT)', districts: ['Dadra & Nagar Haveli'] },
  { state: 'Daman and Diu (UT)', districts: ['Daman','Diu'] },
  { state: 'Delhi (NCT)', districts: ['Central Delhi','East Delhi','New Delhi','North Delhi','North East Delhi','North West Delhi','Shahdara','South Delhi','South East Delhi','South West Delhi','West Delhi'] },
  { state: 'Goa', districts: ['North Goa','South Goa'] },
  { state: 'Gujarat', districts: ['Ahmedabad','Amreli','Anand','Aravalli','Banaskantha','Bharuch','Bhavnagar','Botad','Chhota Udepur','Dahod','Dangs','Devbhoomi Dwarka','Gandhinagar','Gir Somnath','Jamnagar','Junagadh','Kachchh','Kheda','Mahisagar','Mehsana','Morbi','Narmada','Navsari','Panchmahal','Patan','Porbandar','Rajkot','Sabarkantha','Surat','Surendranagar','Tapi','Vadodara','Valsad'] },
  { state: 'Haryana', districts: ['Ambala','Bhiwani','Charkhi Dadri','Faridabad','Fatehabad','Gurgaon','Hisar','Jhajjar','Jind','Kaithal','Karnal','Kurukshetra','Mahendragarh','Mewat','Palwal','Panchkula','Panipat','Rewari','Rohtak','Sirsa','Sonipat','Yamunanagar'] },
  { state: 'Himachal Pradesh', districts: ['Bilaspur','Chamba','Hamirpur','Kangra','Kinnaur','Kullu','Lahaul & Spiti','Mandi','Shimla','Sirmaur','Solan','Una'] },
  { state: 'Jammu and Kashmir', districts: ['Anantnag','Bandipore','Baramulla','Budgam','Doda','Ganderbal','Jammu','Kargil','Kathua','Kishtwar','Kulgam','Kupwara','Leh','Poonch','Pulwama','Rajouri','Ramban','Reasi','Samba','Shopian','Srinagar','Udhampur'] },
  { state: 'Jharkhand', districts: ['Bokaro','Chatra','Deoghar','Dhanbad','Dumka','East Singhbhum','Garhwa','Giridih','Godda','Gumla','Hazaribag','Jamtara','Khunti','Koderma','Latehar','Lohardaga','Pakur','Palamu','Ramgarh','Ranchi','Sahibganj','Seraikela-Kharsawan','Simdega','West Singhbhum'] },
  { state: 'Karnataka', districts: ['Bagalkot','Ballari','Belagavi','Bengaluru Rural','Bengaluru Urban','Bidar','Chamarajanagar','Chikballapur','Chikkamagaluru','Chitradurga','Dakshina Kannada','Davangere','Dharwad','Gadag','Hassan','Haveri','Kalaburagi','Kodagu','Kolar','Koppal','Mandya','Mysuru','Raichur','Ramanagara','Shivamogga','Tumakuru','Udupi','Uttara Kannada','Vijayapura','Yadgir'] },
  { state: 'Kerala', districts: ['Alappuzha','Ernakulam','Idukki','Kannur','Kasaragod','Kollam','Kottayam','Kozhikode','Malappuram','Palakkad','Pathanamthitta','Thiruvananthapuram','Thrissur','Wayanad'] },
  { state: 'Lakshadweep (UT)', districts: ['Agatti','Amini','Androth','Bithra','Chethlath','Kavaratti','Kadmath','Kalpeni','Kilthan','Minicoy'] },
  { state: 'Madhya Pradesh', districts: ['Agar Malwa','Alirajpur','Anuppur','Ashoknagar','Balaghat','Barwani','Betul','Bhind','Bhopal','Burhanpur','Chhatarpur','Chhindwara','Damoh','Datia','Dewas','Dhar','Dindori','Guna','Gwalior','Harda','Hoshangabad','Indore','Jabalpur','Jhabua','Katni','Khandwa','Khargone','Mandla','Mandsaur','Morena','Narsinghpur','Neemuch','Panna','Raisen','Rajgarh','Ratlam','Rewa','Sagar','Satna','Sehore','Seoni','Shahdol','Shajapur','Sheopur','Shivpuri','Sidhi','Singrauli','Tikamgarh','Ujjain','Umaria','Vidisha'] },
  { state: 'Maharashtra', districts: ['Ahmednagar','Akola','Amravati','Aurangabad','Beed','Bhandara','Buldhana','Chandrapur','Dhule','Gadchiroli','Gondia','Hingoli','Jalgaon','Jalna','Kolhapur','Latur','Mumbai City','Mumbai Suburban','Nagpur','Nanded','Nandurbar','Nashik','Osmanabad','Palghar','Parbhani','Pune','Raigad','Ratnagiri','Sangli','Satara','Sindhudurg','Solapur','Thane','Wardha','Washim','Yavatmal'] },
  { state: 'Manipur', districts: ['Bishnupur','Chandel','Churachandpur','Imphal East','Imphal West','Jiribam','Kakching','Kamjong','Kangpokpi','Noney','Pherzawl','Senapati','Tamenglong','Tengnoupal','Thoubal','Ukhrul'] },
  { state: 'Meghalaya', districts: ['East Garo Hills','East Jaintia Hills','East Khasi Hills','North Garo Hills','Ri Bhoi','South Garo Hills','South West Garo Hills','South West Khasi Hills','West Garo Hills','West Jaintia Hills','West Khasi Hills'] },
  { state: 'Mizoram', districts: ['Aizawl','Champhai','Kolasib','Lawngtlai','Lunglei','Mamit','Saiha','Serchhip'] },
  { state: 'Nagaland', districts: ['Dimapur','Kiphire','Kohima','Longleng','Mokokchung','Mon','Peren','Phek','Tuensang','Wokha','Zunheboto'] },
  { state: 'Odisha', districts: ['Angul','Balangir','Balasore','Bargarh','Bhadrak','Boudh','Cuttack','Deogarh','Dhenkanal','Gajapati','Ganjam','Jagatsinghapur','Jajpur','Jharsuguda','Kalahandi','Kandhamal','Kendrapara','Kendujhar','Khordha','Koraput','Malkangiri','Mayurbhanj','Nabarangpur','Nayagarh','Nuapada','Puri','Rayagada','Sambalpur','Sonepur','Sundargarh'] },
  { state: 'Puducherry (UT)', districts: ['Karaikal','Mahe','Pondicherry','Yanam'] },
  { state: 'Punjab', districts: ['Amritsar','Barnala','Bathinda','Faridkot','Fatehgarh Sahib','Fazilka','Ferozepur','Gurdaspur','Hoshiarpur','Jalandhar','Kapurthala','Ludhiana','Mansa','Moga','Muktsar','Nawanshahr','Pathankot','Patiala','Rupnagar','Mohali','Sangrur','Tarn Taran'] },
  { state: 'Rajasthan', districts: ['Ajmer','Alwar','Banswara','Baran','Barmer','Bharatpur','Bhilwara','Bikaner','Bundi','Chittorgarh','Churu','Dausa','Dholpur','Dungarpur','Hanumangarh','Jaipur','Jaisalmer','Jalore','Jhalawar','Jhunjhunu','Jodhpur','Karauli','Kota','Nagaur','Pali','Pratapgarh','Rajsamand','Sawai Madhopur','Sikar','Sirohi','Sri Ganganagar','Tonk','Udaipur'] },
  { state: 'Sikkim', districts: ['East Sikkim','North Sikkim','South Sikkim','West Sikkim'] },
  { state: 'Tamil Nadu', districts: ['Ariyalur','Chennai','Coimbatore','Cuddalore','Dharmapuri','Dindigul','Erode','Kanchipuram','Kanyakumari','Karur','Krishnagiri','Madurai','Nagapattinam','Namakkal','Nilgiris','Perambalur','Pudukkottai','Ramanathapuram','Salem','Sivaganga','Thanjavur','Theni','Thoothukudi','Tiruchirappalli','Tirunelveli','Tiruppur','Tiruvallur','Tiruvannamalai','Tiruvarur','Vellore','Viluppuram','Virudhunagar'] },
  { state: 'Telangana', districts: ['Adilabad','Bhadradri Kothagudem','Hyderabad','Jagtial','Jangaon','Jayashankar Bhoopalpally','Jogulamba Gadwal','Kamareddy','Karimnagar','Khammam','Komaram Bheem Asifabad','Mahabubabad','Mahabubnagar','Mancherial','Medak','Medchal','Nagarkurnool','Nalgonda','Nirmal','Nizamabad','Peddapalli','Rajanna Sircilla','Rangareddy','Sangareddy','Siddipet','Suryapet','Vikarabad','Wanaparthy','Warangal Rural','Warangal Urban','Yadadri Bhuvanagiri'] },
  { state: 'Tripura', districts: ['Dhalai','Gomati','Khowai','North Tripura','Sepahijala','South Tripura','Unakoti','West Tripura'] },
  { state: 'Uttar Pradesh', districts: ['Agra','Aligarh','Allahabad','Ambedkar Nagar','Amethi','Amroha','Auraiya','Azamgarh','Baghpat','Bahraich','Ballia','Balrampur','Banda','Barabanki','Bareilly','Basti','Bhadohi','Bijnor','Budaun','Bulandshahr','Chandauli','Chitrakoot','Deoria','Etah','Etawah','Faizabad','Farrukhabad','Fatehpur','Firozabad','Gautam Buddha Nagar','Ghaziabad','Ghazipur','Gonda','Gorakhpur','Hamirpur','Hapur','Hardoi','Hathras','Jalaun','Jaunpur','Jhansi','Kannauj','Kanpur Dehat','Kanpur Nagar','Kasganj','Kaushambi','Kushinagar','Lakhimpur Kheri','Lalitpur','Lucknow','Maharajganj','Mahoba','Mainpuri','Mathura','Mau','Meerut','Mirzapur','Moradabad','Muzaffarnagar','Pilibhit','Pratapgarh','Raebareli','Rampur','Saharanpur','Sambhal','Sant Kabir Nagar','Shahjahanpur','Shamli','Shravasti','Siddharthnagar','Sitapur','Sonbhadra','Sultanpur','Unnao','Varanasi'] },
  { state: 'Uttarakhand', districts: ['Almora','Bageshwar','Chamoli','Champawat','Dehradun','Haridwar','Nainital','Pauri Garhwal','Pithoragarh','Rudraprayag','Tehri Garhwal','Udham Singh Nagar','Uttarkashi'] },
  { state: 'West Bengal', districts: ['Alipurduar','Bankura','Birbhum','Cooch Behar','Dakshin Dinajpur','Darjeeling','Hooghly','Howrah','Jalpaiguri','Jhargram','Kalimpong','Kolkata','Malda','Murshidabad','Nadia','North 24 Parganas','Paschim Bardhaman','Paschim Medinipur','Purba Bardhaman','Purba Medinipur','Purulia','South 24 Parganas','Uttar Dinajpur'] },
];

const ALL_STATES = INDIA_STATE_DISTRICT_DATA.map(s => s.state);

// ──────────────────────────────────────────────
// REUSABLE DROPDOWN COMPONENT
// ──────────────────────────────────────────────
function DropdownPicker({
  label,
  value,
  options,
  placeholder,
  onSelect,
  hasError,
  disabled = false,
}: {
  label: string;
  value: string;
  options: string[];
  placeholder: string;
  onSelect: (val: string) => void;
  hasError?: boolean;
  disabled?: boolean;
}) {
  const [visible, setVisible] = useState(false);
  const [search, setSearch] = useState('');

  const filtered = options.filter(o =>
    o.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <Text style={styles.label}>{label}</Text>
      <TouchableOpacity
        style={[styles.dropdown, hasError && styles.inputError, disabled && styles.dropdownDisabled]}
        onPress={() => { if (!disabled) { setSearch(''); setVisible(true); } }}
        activeOpacity={disabled ? 1 : 0.7}
      >
        <Text style={[styles.dropdownText, !value && styles.dropdownPlaceholder]}>
          {value || placeholder}
        </Text>
        <Text style={styles.dropdownArrow}>▾</Text>
      </TouchableOpacity>

      <Modal visible={visible} transparent animationType="slide" onRequestClose={() => setVisible(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalSheet}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{label}</Text>
              <TouchableOpacity onPress={() => setVisible(false)}>
                <Text style={styles.modalClose}>✕</Text>
              </TouchableOpacity>
            </View>

            {/* SEARCH BAR */}
            <TextInput
              style={styles.modalSearch}
              placeholder={`Search ${label.toLowerCase()}...`}
              value={search}
              onChangeText={setSearch}
              autoFocus
            />

            <FlatList
              data={filtered}
              keyExtractor={(item) => item}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[styles.modalItem, item === value && styles.modalItemActive]}
                  onPress={() => { onSelect(item); setVisible(false); }}
                >
                  <Text style={[styles.modalItemText, item === value && styles.modalItemTextActive]}>
                    {item}
                  </Text>
                  {item === value && <Text style={styles.checkmark}>✓</Text>}
                </TouchableOpacity>
              )}
              keyboardShouldPersistTaps="handled"
            />
          </View>
        </View>
      </Modal>
    </>
  );
}

// ──────────────────────────────────────────────
// MAIN REGISTER SCREEN
// ──────────────────────────────────────────────
export default function RegisterScreen({ navigation }: any) {
  const { register } = useAuth();

  const [form, setForm] = useState({
    name: '',
    phone: '',
    password: '',
    location_state: '',
    location_district: '',
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const update = (key: string, value: string) => {
    if (key === 'location_state') {
      // Reset district when state changes
      setForm(f => ({ ...f, location_state: value, location_district: '' }));
    } else {
      setForm(f => ({ ...f, [key]: value }));
    }
    setErrors(e => ({ ...e, [key]: '', district: '' }));
  };

  const getDistricts = (): string[] => {
    const found = INDIA_STATE_DISTRICT_DATA.find(s => s.state === form.location_state);
    return found ? found.districts : [];
  };

  // ✅ VALIDATION
  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (form.name.trim().length < 2)
      newErrors.name = 'Name must be at least 2 characters';

    if (!/^[6-9]\d{9}$/.test(form.phone))
      newErrors.phone = 'Enter valid 10-digit mobile number';

    if (form.password.length < 4)
      newErrors.password = 'Password must be at least 4 characters';

    if (!form.location_state)
      newErrors.location_state = 'Please select your state';

    if (!form.location_district)
      newErrors.district = 'Please select your district';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ✅ REGISTER HANDLER
  const handleRegister = async () => {
    if (!validate()) return;

    const cleanPhone = form.phone.replace(/\D/g, '');

    if (cleanPhone.length !== 10) {
      Alert.alert('Invalid Number', 'Enter valid 10-digit mobile number');
      return;
    }

    setLoading(true);

    try {
      await register({
        name: form.name.trim(),
        phone: cleanPhone,
        password: form.password,
        location_state: form.location_state,
        location_district: form.location_district,
        language: 'en',
        crops: [],
      });

      Alert.alert('Success 🎉', 'Account created successfully!');
      navigation.replace('MainTabs');

    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Registration failed. Please try again.';
      Alert.alert('Registration Failed', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <StatusBar barStyle="light-content" backgroundColor={COLORS.primaryDark} />

      <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>

        <LinearGradient colors={[COLORS.primaryDark, COLORS.primary]} style={styles.header}>
          <Text style={styles.logo}>👨‍🌾</Text>
          <Text style={styles.headerTitle}>Create Account</Text>
          <Text style={styles.headerSubtitle}>Join thousands of smart farmers</Text>
        </LinearGradient>

        <View style={styles.card}>

          {/* NAME */}
          <Text style={styles.label}>Full Name</Text>
          <TextInput
            style={[styles.input, errors.name ? styles.inputError : undefined]}
            placeholder="Ramesh Kumar"
            value={form.name}
            onChangeText={(v) => update('name', v)}
          />
          {errors.name && <Text style={styles.errorText}>{errors.name}</Text>}

          {/* PHONE */}
          <Text style={styles.label}>Mobile Number</Text>
          <View style={[styles.phoneWrapper, errors.phone ? styles.inputError : undefined]}>
            <Text style={styles.phonePrefix}>+91</Text>
            <TextInput
              style={styles.phoneInput}
              placeholder="9876543210"
              keyboardType="number-pad"
              maxLength={10}
              value={form.phone}
              onChangeText={(v) => {
                const onlyNumbers = v.replace(/\D/g, '');
                update('phone', onlyNumbers);
              }}
            />
          </View>
          {errors.phone && <Text style={styles.errorText}>{errors.phone}</Text>}

          {/* PASSWORD */}
          <Text style={styles.label}>Password</Text>
          <TextInput
            style={[styles.input, errors.password ? styles.inputError : undefined]}
            placeholder="Min 4 characters"
            secureTextEntry
            value={form.password}
            onChangeText={(v) => update('password', v)}
          />
          {errors.password && <Text style={styles.errorText}>{errors.password}</Text>}

          {/* STATE DROPDOWN */}
          <DropdownPicker
            label="State"
            value={form.location_state}
            options={ALL_STATES}
            placeholder="Select your state"
            onSelect={(v) => update('location_state', v)}
            hasError={!!errors.location_state}
          />
          {errors.location_state && <Text style={styles.errorText}>{errors.location_state}</Text>}

          {/* DISTRICT DROPDOWN */}
          <DropdownPicker
            label="District"
            value={form.location_district}
            options={getDistricts()}
            placeholder={form.location_state ? 'Select your district' : 'Select state first'}
            onSelect={(v) => update('location_district', v)}
            hasError={!!errors.district}
            disabled={!form.location_state}
          />
          {errors.district && <Text style={styles.errorText}>{errors.district}</Text>}

          {/* REGISTER BUTTON */}
          <TouchableOpacity style={styles.btn} onPress={handleRegister} disabled={loading}>
            {loading
              ? <ActivityIndicator color="#fff" />
              : <Text style={styles.btnText}>Register 🌱</Text>
            }
          </TouchableOpacity>

        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollContent: { paddingBottom: 40 },

  header: { padding: 40, alignItems: 'center' },
  logo: { fontSize: 50 },
  headerTitle: { color: 'white', fontSize: 24, fontWeight: 'bold' },
  headerSubtitle: { color: 'white' },

  card: { padding: 20 },

  label: { marginTop: 14, fontWeight: '600', marginBottom: 4 },

  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 12,
    borderRadius: 8,
  },

  inputError: { borderColor: 'red' },
  errorText: { color: 'red', fontSize: 12, marginTop: 3 },

  phoneWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
  },
  phonePrefix: { marginRight: 10, fontWeight: '600' },
  phoneInput: { flex: 1 },

  // ── DROPDOWN ──
  dropdown: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fff',
  },
  dropdownDisabled: { backgroundColor: '#f5f5f5' },
  dropdownText: { fontSize: 15, color: '#222', flex: 1 },
  dropdownPlaceholder: { color: '#aaa' },
  dropdownArrow: { color: '#666', fontSize: 16 },

  // ── MODAL ──
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.45)',
    justifyContent: 'flex-end',
  },
  modalSheet: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
    paddingBottom: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderColor: '#eee',
  },
  modalTitle: { fontSize: 17, fontWeight: '700' },
  modalClose: { fontSize: 20, color: '#666', paddingHorizontal: 6 },
  modalSearch: {
    margin: 12,
    padding: 10,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    fontSize: 14,
    backgroundColor: '#fafafa',
  },
  modalItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 13,
    paddingHorizontal: 20,
    borderBottomWidth: 0.5,
    borderColor: '#f0f0f0',
  },
  modalItemActive: { backgroundColor: '#e8f5e9' },
  modalItemText: { fontSize: 15, color: '#333', flex: 1 },
  modalItemTextActive: { color: 'green', fontWeight: '600' },
  checkmark: { color: 'green', fontSize: 16 },

  btn: {
    backgroundColor: 'green',
    padding: 15,
    marginTop: 24,
    borderRadius: 10,
    alignItems: 'center',
  },
  btnText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
});